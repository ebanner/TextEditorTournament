import connection

class ParticipantConnection(connection.Connection):
    """
    tbd
    
    """
    def __init__(self, socket, boss):
        """ """
        super(ParticipantConnection, self).__init__(socket, boss)
        self.ready = False
        self.challenge_accepted = False
        # True when the participant is working on a problem
        self.working = False
        # Only True when the participant has forfeited
        self.forfeited = False
        
    def init_challenge(self, challenge):
        """Send challenge information to each client."""
        self.write_line('CHALLENGE_INITIATE')
        print('Sent init to a participant')
        self.write_line(str(challenge.id))
        print('Sent id to a paricipant')
        self.write_line(challenge.name)
        print('Sent name to a participant')
        self.write_line(str(len(challenge.description)))
        print('Sent # of lines = {}'.format(len(challenge.description)))
        for line in challenge.description:
            print(line)
            self.write_line(line)
        print('Sent description (line by line)')
        
        self.ready = False
        
    def start_challenge(self, challenge):
        """ """
        self.write_line('CHALLENGE_START')
        self.write_files(challenge.start_files)
        self.working = True
        
    def process_challenge_submission(self):
        pass

    def process_challenge_forfeit(self):
        pass

    def process_challenge_reset(self):
        pass

    def cancel_challenge(self):
        """The challenge is cancelled, so break out of challenge mode."""
        self.write_line('CHALLENGE_CANCEL')
        print('Challenge CANCELLED')
    
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
        elif message == 'CHALLENGE_SUBMISSION':
            pass
        elif message == 'CHALLENGE_FORFEIT':
            pass
        elif message == 'CHALLENGE_RESET':
            pass
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
