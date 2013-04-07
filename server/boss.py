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
