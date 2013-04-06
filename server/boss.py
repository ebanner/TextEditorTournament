# 

import participant
import manager

class Boss():
    """ hello
    
    """
    def __init__(self):
        self.participants = []
        
    def add_participant(self, client_sock):
        p = participant.Participant(client_sock)
        p.start()
        self.participants.append(p)
        print('Client added')
        
    def set_manager(self, client_sock):
        mngr = manager.Manager(client_sock)
        if not hasattr(self, 'manager'):
            mngr.start()
            self.manager = mngr
            print('Manager added')
        else:
            mngr.write_line("ERROR: Manager already exists. Rejected.");
            mngr.close()
            print('Manager rejected (one already exists)')
