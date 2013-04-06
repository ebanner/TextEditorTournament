# manager.py
import client

class Manager(client.Client):
    """
    tbd
    
    """
    def check_message(self, message):
        """ """
        super(Manager, self).check_message(message)
        print(message)
        
    def run(self):
        """ """
        super(Manager, self).run()
