# 

from participant_connection import ParticipantConnection
from manager_connection import ManagerConnection

class Boss():
    """
    hello
    
    """
    def __init__(self):
        self.participants = []
        self.challenge_active = False
        self.challenge = None
    
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
    
    def add_participant(self, client_sock):
        p = ParticipantConnection(client_sock, self)
        p.start()
        self.participants.append(p)
        print('Client added')
        
    def set_manager(self, client_sock):
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
        return 0
        
        
        
        
        
        
        
        
        
        
