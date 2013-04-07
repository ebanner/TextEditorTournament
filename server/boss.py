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
            
    def run_challenge(self):
        """Send the current challenge files to all participants"""
        if not self.challenge or self.challenge_active:
            print('Either no challenge submitted or challenge is already going ' 
            'on')
            return False
        for participant in participants:
            # send start files to each participant
            participant.send_challenge(self.challenge)
            
        return True
        
        
        
        
        
        
        
        
        
        
