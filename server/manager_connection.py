# manager.py
import connection
import challenge

class ManagerConnection(connection.Connection):
    """
    tbd
    
    """
    def check_message(self, message):
        """Check the incoming message to see which activity the manager would
        like to engage in"""
        #print(message)
        if message == 'CHALLENGE_SEND_BEGIN':
            self.process_challenge_request()
        elif message == 'CHALLENGE_INITIATE':
            self.process_challenge_init_request()
        elif message == 'CHALLENGE_START':
            self.process_challenge_start()
        elif message == 'CHALLENGE_CANCEL':
            self.process_challenge_cancel()
        else:
            super(ManagerConnection, self).check_message(message)

    def process_challenge_start(self):
        """Have the boss tell participants to start the challenge"""
        self.boss.start_challenge()

    def process_challenge_cancel(self):
        """Have the boss tell participants to cancel the challenge"""
        self.boss.cancel_challenge()
            
    def process_challenge_request(self):
        """Receive challenge material from manager and give the challenge to the
        boss.

        This connection receives all the material for a challenge, including the
        challenge name, description, and all of the challenge files unless there
        is a challenge currently going on (the boss knows if there is a
        challenge currently underway).

        """
        if self.boss.challenge_active:
            print('Boss rejects challenge request')
            self.write_line('CHALLENGE_REJECTED')
            return
        
        self.write_line('CHALLENGE_ACCEPTED')
        # Receive challenge id, challenge name, number of lines in descirption, 
        # description, and tarred file
        challenge_id = self.read_line()
        print(challenge_id)
        challenge_name = self.read_line()
        print(challenge_name)
        description_line_count = int(self.read_line())
        print(description_line_count)
        
        description = []
        for i in range(description_line_count):
            line = self.read_line()
            description.append(line)
            
        # Begin file transmission
        message = self.read_line()
        if message != 'FILE_TRANSMISSION_BEGIN':
            print('Expected FILE_TRANSMISSION_BEGIN message, '
                'but got {} instead.'.format(message))
            return
        
        # Grab the lines
        files = self.read_files()
        
        print('files received')
        # Create the challenge object with all of the information and data
        new_challenge = challenge.Challenge(challenge_id, challenge_name,
            description, files)
        self.boss.challenge = new_challenge
        print('boss equipped with challenge')
            
        # Everything went well, so send OK to manager
        self.write_line('CHALLENGE_OKAY')
    
    def process_challenge_init_request(self):
        """
        Tells the Boss to initiate a challenge. Depending on the return value
        from the Boss, send the appropriate response to the manager.
        """
        if not self.boss.challenge:
            self.write_line('CHALLENGE_NOT_FOUND')
            return
        
        # Use retval to check for possible errors, and report back
        retval = self.boss.init_challenge()
        
        if retval == 0: # All is well
            self.boss.challenge_active = True
            
        elif retval == 1: # No challenge was loaded/sent yet
            self.write_line('CHALLENGE_NOT_FOUND')
            
        elif retval == 2: # Another challenge is already going on
            self.write_line('CHALLENGE_ALREADY_ACTIVE')
            
        elif retval == 3: # No participants currently conneted
            self.write_line('NO_PARTICIPANTS_CONNECTED')
            
        else: # some other error
            self.write_line('CHALLENGE_ERROR')
    
    def send_participant_accept_message(self, name, editor):
        """Sends a message saying that a participant accepted a challenge."""
        self.write_line('PARTICIPANT_ACCEPTED')
        self.write_line(name)
        self.write_line(editor)
    
    def send_challenge_ready(self, n_part_accepting, n_part_total):
        """
        Sends a message indicating that all participants have responded in
        accepting or rejecting a challenge, and how many of a total number of
        participants have chosen to accept the challenge.
        """
        print('IN SEND_CHALLENGE_READY')
        self.write_line('PARTICIPANT_LIST_FINISHED')
        self.write_line(str(n_part_accepting))
        self.write_line(str(n_part_total))
    
    def send_challenge_finished(self):
        self.write_line('CHALLENGE_FINISH')
        
    def run(self):
        """ """
        self.write_line("CONNECTION_ACCEPTED")
        super(ManagerConnection, self).run()
    
    def close(self):
        super(ManagerConnection, self).close()
        # remove from boss
        delattr(self.boss, 'manager')
