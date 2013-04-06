# participant.py
import connection

class ParticipantConnection(connection.Connection):
    """
    tbd
    
    """
    def check_message(self, message):
        """ """
        print(message)
        super(ParticipantConnection, self).check_message(message)
    
    def run(self):
        """ """
        self.write_line("CONNECTION_ACCEPTED")
        self.user = self.read_line()
        self.editor = self.read_line()
        print(self.user)
        print(self.editor)
        super(ParticipantConnection, self).run()
