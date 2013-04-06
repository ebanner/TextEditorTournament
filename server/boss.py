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
        print('in setmngr')
        mngr = manager.Manager(client_sock)
        print('after constructor')
        if not hasattr(self, 'manager'):
            print('before add')
            mngr.start()
            print('before add')
            self.manager = mngr
            print('Manager added')
        else:
            print('before reject')
            mngr.close()
            print('manager not added')
