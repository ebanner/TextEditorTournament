# 

import participant

class Boss():
    """ hello
    
    """
    def __init__(self):
        self.participants = []
        
    def add_participant(self, client_sock):
        p = participant.Participant(client_sock)
        p.run()
        self.participants.append(p)
        print('Client added')
