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
        """Send over the signal to start the challenge only if the user has
        accepted the challenge."""
        if self.challenge_accepted:
            self.write_line('CHALLENGE_START')
            self.write_files(challenge.start_files)
            self.working = True
        
    def process_challenge_submission(self):
        """Grade challenge submission and return either
        CHALLENGE_RESULTS_CORRECT or CHALLENGE_RESULTS_INCORRECT"""
        message = self.read_line()
        print('Challenge ID: {}'.format(int(message)))
        message = self.read_line()
        assert message == 'FILE_TRANSMISSION_BEGIN'

        # Read in files submitted by the participant
        submission_files = self.read_files()
        # Get the diff of the files and the total number of lines
        diffs, num_lines = self.boss.check_solution(submission_files)

        if diffs:
            # Send over the number of lines in the diff and the diff itself
            self.write_line('CHALLENGE_RESULTS_INCORRECT')
            self.write_line(str(num_lines))
            for diff in diffs:
                for line in diff:
                    self.write_line(line)
        else:
            # Signal that we got the correct answer
            self.working = False
            self.write_line('CHALLENGE_RESULTS_CORRECT')

        # We are not forfeiting, just letting the boss know that we
        # have made an attempt at solving the problem.
        self.boss.challenge_start_response(self)

    def process_challenge_forfeit(self):
        print("We're forfeiting!!!! It's over Johnny!")
        self.forfeited = True
        # Tell the boss we are forfeiting and have it check to see if
        # everyone if done.
        self.boss.challenge_start_response(self)

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
            self.process_challenge_submission()
        elif message == 'CHALLENGE_FORFEIT':
            self.process_challenge_forfeit()
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
