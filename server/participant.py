# participant.py
import client

class Participant(client.Client):
    """
    tbd
    
    """
    def check_message(self, message):
        """ """
        super(Participant, self).check_message(message)
        print(message)
    
    def run(self):
        """ """
        self.user = self.read_line()
        self.editor = self.read_line()
        
        super(Participant, self).run()
