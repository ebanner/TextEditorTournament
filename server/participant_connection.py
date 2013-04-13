# participant.py
import connection

class ParticipantConnection(connection.Connection):
    """
    tbd
    
    """
    def __init__(self, socket, boss):
        """ """
        super(ParticipantConnection, self).__init__(socket, boss)
        self.state = 0
        self.ready = False
        self.challenge_accepted = False
        
    def init_challenge(self, challenge):
        """Send challenge information to each client."""
        self.write_line('CHALLENGE_INITIATE')
        print('sent init')
        self.write_line(str(challenge.id))
        print('sent id')
        self.write_line(challenge.name)
        print('sent name')
        self.write_line(str(len(challenge.description)))
        print('sent # of lines = {}'.format(len(challenge.description)))
        for line in challenge.description:
            self.write_line(line)
        print('sent description (line by line)')
        
        self.state = 1
        self.ready = False
        print('sent info, state changed to 1')
        
    def start_challenge(self, challenge):
        """ """
        print('Challenge START CALLED')
    
    def accept_challenge(self, choice):
        """
        Sets the choice of the participant to variables, and updates the
        Boss's status.
        """
        self.ready = True
        self.challenge_accepted = choice
        self.boss.challenge_init_response(self)
        if choice:
            print('challenge ACCEPTED by client')
        else:
            print('challenge REJECTED by client')
                
    def check_message(self, message):
        """Listen to incomming messages and call the appropriate functions."""
        if message == 'CHALLENGE_ACCEPTED':
            self.accept_challenge(True)
        elif message == 'CHALLENGE_REJECTED':
            self.accept_challenge(False)
        else:
            print(message)
        super(ParticipantConnection, self).check_message(message)
    
    # TODO - make sure closed flags a variable so that boss knows if DC'd
    
    def run(self):
        """Runs this thread (the participant connection thread)."""
        self.write_line("CONNECTION_ACCEPTED")
        self.user = self.read_line()
        self.editor = self.read_line()
        print(self.user)
        print(self.editor)
        super(ParticipantConnection, self).run()
