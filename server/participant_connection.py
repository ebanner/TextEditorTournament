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
        # Send participant to display
        if self.boss.display:
            self.boss.send_participant_to_display(self.user, self.editor)
        super(ParticipantConnection, self).run()
