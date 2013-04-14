# boss.py

import threading
from participant_connection import ParticipantConnection
from manager_connection import ManagerConnection

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
        self.state = 0 # initial state, normal
        self.thread_lock = threading.Lock()
    
    def check_solution(self, files):
        # check if challenge exists
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
            
        # if everyone is done
        #   self.manager.finish_challenge()
    
    def challenge_init_response(self, responder):
        """
        STATE 1 method: RUN_STATE_CHALLENGE_INIT
            --- if not in correct state, does nothing
        SYNCHRONIZED: Called by each participant tread ndividually.
        Tells manager about the participant that responded as ready, and checks
        all other participants. If all are ready, the challenge init phase is
        over, and the manager is notified.
        """
        if self.state != RUN_STATE_CHALLENGE_INIT:
            return
        
        ##### Syncrhonize threads. #####
        self.thread_lock.acquire()
        
        print("In thread lock...")
        
        # Tell the manager about who responded (if they accepted).
        if responder.challenge_accepted:
            print("Participant accepted.")
            self.manager.send_participant_accept_message(responder.user,
                responder.editor)
        
        # Check if every participant is active.
        all_ready = False
        num_accepting = 0
        for participant in self.participants:
            all_ready = all_ready or participant.ready or participant.closed
            if participant.challenge_accepted:
                num_accepting = num_accepting + 1
        
        # If everyone is ready, tell manager about it and move on to next phase.
        if all_ready:
            print("Everyone is ready")
            # If manager confirms (True is returned), then start the challenge.
            confirm = self.manager.send_challenge_ready(num_accepting,
                len(self.participants))
            if confirm: # If confirmed, send all participants the files and go.
                self.phase = RUN_STATE_CHALLENGE_MODE
                for participant in self.participants:
                    participant.start_challenge(self.challenge)
            else: # Otherwise, tell participants to abort challenge.
                self.phase = RUN_STATE_NORMAL
                for participant in self.participants:
                    participant.cancel_challenge()
        
        self.thread_lock.release()
        ##### Thread synchronization done. #####
        
        print("Out of thread lock...")
        
    
    def add_participant(self, client_sock):
        """
        Use the given socket to create a Participant connection object, and
        adds that participant connection to the list of connected participants.
        """
        p = ParticipantConnection(client_sock, self)
        p.start()
        self.participants.append(p)
        print('Client added')
        
    def set_manager(self, client_sock):
        """
        If there is is not already a manager connected, set the
        given socket to be a new Manager connection.
        """
        mngr = ManagerConnection(client_sock, self)
        if not hasattr(self, 'manager'):
            mngr.start()
            self.manager = mngr
            print('Manager added')
        else:
            mngr.write_line("ERROR: Manager already exists. Rejected.");
            mngr.close()
            print('Manager rejected (one already exists)')
            
    def init_challenge(self):
        """
        Send the current challenge files to all participants
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
            # send start files to each participant
            participant.init_challenge(self.challenge)
        self.state = RUN_STATE_CHALLENGE_INIT # waiting for participants
        return 0
