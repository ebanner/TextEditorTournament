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
        # Check if challenge exists
        num_solved = 0
        diffs = []
        for f in files:
            diff, solved = self.challenge.check_file(f)
            if solved:
                num_solved += 1
            diffs.append(diff)
        if num_solved == self.challenge.num_solutions:
            pass #win
        else:
            pass #reply incorrect message
            
        # If everyone is done
        #   self.manager.finish_challenge()
    
    def challenge_start_response(self, responder, forfeiting):
        """
        STATE 2 method: 
            --- if not in correct state, does nothing
        SYNCHRONIZED: Called by each participant thread individually.
        Tells manager about the participant's result, and checks other
        participants. If all are done, then the challenge is over, and the
        manager is notified.

        """
        if self.state != RUN_STATE_CHALLENGE_MODE:
            print('Current state: {}. Expecting {}'.format(self.state,
                RUN_STATE_CHALLENGE_MODE))
            return

        ##### Syncrhonize threads. #####
        self.thread_lock.acquire()
        
        print("In thread lock...")
        if responder.forfeited:
            print("Participant forfeited.")
            self.display.send_participant_forfeit_message(responder.user)

        # Check if every participant is finished.
        all_finished = False
        num_finished = 0
        for participant in self.participants:
            all_finished = all_finished or participant.forfeited\
                    or not participent.working or participant.closed
            if participant.forfeited or not participant.working:
                num_finished += 1
        
        # If everyone is finished, tell manager and display about it so we can
        # end the challenge.
        if all_finished:
            print("Everyone is finished")
            self.display.send_challenge_finished()
            self.manager.send_challenge_finished()

        self.thread_lock.release()
        ##### Thread synchronization done. #####
        print("Out of thread lock...")

        # Go back to the challenge init state
        self.state = RUN_STATE_CHALLENGE_INIT
        self.challenge_active = False

    def challenge_init_response(self, responder):
        """
        STATE 1 method: RUN_STATE_CHALLENGE_INIT
            --- if not in correct state, does nothing
        SYNCHRONIZED: Called by each participant thread individually.
        Tells manager about the participant that responded as ready, and checks
        all other participants. If all are ready, the challenge init phase is
        over, and the manager is notified.
        """
        if self.state != RUN_STATE_CHALLENGE_INIT:
            return
        
        ##### Syncrhonize threads. #####
        self.thread_lock.acquire()
        
        print("In thread lock...")
        
        # Tell the manager and display about who responded (if they accepted).
        if responder.challenge_accepted:
            print("Participant accepted.")
            self.manager.send_participant_accept_message(responder.user,
                responder.editor)
            self.display.send_participant_accept_message(responder.user,
                responder.editor)
        
        # Check if every participant is active.
        all_ready = False
        num_accepting = 0
        for participant in self.participants:
            all_ready = all_ready or participant.ready or participant.closed
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
