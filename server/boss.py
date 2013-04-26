# boss.py

import threading
from participant_connection import ParticipantConnection
from manager_connection import ManagerConnection
from display_connection import DisplayConnection

RUN_STATE_NORMAL = 0
RUN_STATE_CHALLENGE_INIT = 1
RUN_STATE_CHALLENGE_MODE = 2

class Boss():
    """
    hello
    
    """
    def __init__(self):
        self.participants = []
        self.challenge_active = False
        self.challenge = None
        self.state = RUN_STATE_NORMAL # initial state, normal
        self.thread_lock = threading.Lock()
        self.display = None
    
    def check_solution(self, files):
        """Compute the diff of the submitted files vs. the solution files for
        the active challenge"""
        num_solved = 0
        diffs = []
        # Keep track of the total number of lines in the diff across all the
        # files.
        num_lines = 0
        for f in files:
            diff = self.challenge.check_file(f)
            if diff == False:
                # The submitted file doesn't have a corresponding *.sol file.
                continue
            elif not diff:
                num_solved += 1
            else:
                assert diff
                # Only append the diff if it differed from the solution file
                diffs.append(diff)
                num_lines += len(diff)
        return diffs, num_lines
            
    def challenge_start_response(self, responder):
        """
        STATE 2 method: 
            --- if not in correct state, does nothing
        SYNCHRONIZED: Called by each participant thread individually.
        Tells manager about the participant's result, and checks other
        participants. If all are done, then the challenge is over, and the
        manager is notified.

        """
        ##### Syncrhonize threads. #####
        self.thread_lock.acquire()

        if self.state != RUN_STATE_CHALLENGE_MODE:
            print('Current state: {}. Expecting {}'.format(self.state,
                RUN_STATE_CHALLENGE_MODE))
            self.thread_lock.release()
            return
        
        print("In thread lock...")
        if responder.forfeited:
            print("Participant forfeited.")
            self.display.send_forfeit_message(responder.user)
        elif responder.working:
            # Inform the display Participant gave an incorrect solution to the
            # challenge.
            self.display.send_incorrect_submission_message(responder.user)
        else:
            assert not responder.working and not responder.forfeited
            # Participant has given correct solution
            self.display.send_finished_message(responder.user)

        # Check if every participant is finished.
        all_finished = True
        num_finished = 0
        for participant in self.participants:
            all_finished = all_finished and (participant.forfeited\
                    or not participant.working or participant.closed\
                    or not participant.challenge_accepted)
            if participant.forfeited or not participant.working:
                num_finished += 1
        
        # If everyone is finished, tell manager and display about it so we can
        # end the challenge.
        if all_finished:
            print("Everyone is finished")
            self.display.send_challenge_finished()
            self.manager.send_challenge_finished()
            # Go back to the challenge init state
            self.state = RUN_STATE_CHALLENGE_INIT
            self.challenge_active = False
            # Update each participant's attributes for the next challenge
            for participant in self.participants:
                participant.ready = False
                participant.forfeited = False

        self.thread_lock.release()
        ##### Thread synchronization done. #####
        print("Out of thread lock...")

    def challenge_init_response(self, responder):
        """
        STATE 1 method: RUN_STATE_CHALLENGE_INIT
            --- if not in correct state, does nothing
        SYNCHRONIZED: Called by each participant thread individually.
        Tells manager about the participant that responded as ready, and checks
        all other participants. If all are ready, the challenge init phase is
        over, and the manager is notified.
        """
        ##### Syncrhonize threads. #####
        self.thread_lock.acquire()
        
        print("In thread lock...")

        if self.state != RUN_STATE_CHALLENGE_INIT:
            self.thread_lock.release()
            return
        
        # Tell the manager and display about who responded (if they accepted).
        if responder.challenge_accepted:
            print("Participant accepted.")
            self.manager.send_participant_accept_message(responder.user,
                responder.editor)
            self.display.send_participant_accept_message(responder.user,
                responder.editor)
        
        # Check if every participant is active.
        all_ready = True
        num_accepting = 0
        for participant in self.participants:
            all_ready = all_ready and (participant.ready or participant.closed)
            if participant.challenge_accepted:
                num_accepting += 1
        
        # If everyone is ready, tell manager about it and move on to next phase.
        if all_ready:
            print("Everyone is ready")
            # If manager confirms (True is returned), then start the challenge.
            self.manager.send_challenge_ready(num_accepting,
                    len(self.participants))

        self.thread_lock.release()
        ##### Thread synchronization done. #####
        print("Out of thread lock...")

    def start_challenge(self):
        """Send all participants the files and go"""
        print('ENTERING RUN_CHALLENGE_MODE')
        self.state = RUN_STATE_CHALLENGE_MODE
        # Send materials over to participants
        for participant in self.participants:
            participant.start_challenge(self.challenge)

        # Inform display the challenge is underway
        self.display.start_challenge()

    def cancel_challenge(self):
        """Tell participants to abort challenge"""
        print('CANCELLING CHALLENGE')
        self.state = RUN_STATE_NORMAL
        self.challenge_active = False
        for participant in self.participants:
            participant.cancel_challenge()

    def add_participant(self, client_sock):
        """Use the given socket to create a Participant connection object, and
        adds that participant connection to the list of connected participants."""
        p = ParticipantConnection(client_sock, self)
        p.start()
        self.participants.append(p)
        print('Client added')
        
    def send_participant_to_display(self, user, editor):
        self.display.send_participant_to_display(user, editor)

    def set_manager(self, client_sock):
        """If there is is not already a manager connected, set the
        given socket to be a new Manager connection."""
        mngr = ManagerConnection(client_sock, self)
        if not hasattr(self, 'manager'):
            mngr.start()
            self.manager = mngr
            print('Manager added')
        else:
            mngr.write_line("ERROR: Manager already exists. Rejected.");
            mngr.close()
            print('Manager rejected (one already exists)')
            
    def set_display(self, client_sock):
        """Use the given socket to create a Display connection object, and
        adds that participant connection to the list of connected participants."""
        display = DisplayConnection(client_sock, self)
        if not self.display:
            # There can only be one display
            display.start()
            self.display = display
            print('Display added')
        else:
            display.write_line("ERROR: Display already exists. Rejected.");
            display.close()
            print('Display rejected (one already exists)')

    def init_challenge(self):
        """Send the current challenge files to all participants.

        RETURNS 0 if challenge was initiallized sucessfully,
                1 if there is no challenge available to init,
                2 if another challenge is already going on,
                3 if no participants are connected.
        """
        if not self.challenge:
            print('No challenge available.')
            return 1
        elif self.challenge_active:
            print('Another challenge is already going on.')
            return 2
        if len(self.participants) == 0:
            print('No participants connected')
            return 3
            
        for participant in self.participants:
            # Send start files to each participant
            participant.init_challenge(self.challenge)
            participant.ready = False
        self.state = RUN_STATE_CHALLENGE_INIT # waiting for participants

        # Send the start files to the display
        self.display.init_challenge(self.challenge)

        return 0
