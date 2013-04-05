# 

class Boss():
    """ hello
    
    """
    def __init__(self):
        self.clients = []
        
    def add_client(self, new_client):
        self.clients.append(new_client)
        print('Client added')
