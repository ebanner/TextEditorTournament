# manager.py
import connection
import challenge

class ManagerConnection(connection.Connection):
    """
    tbd
    
    """
    def check_message(self, message):
        """ """
        print(message)
        if message == 'CHALLENGE_SEND_BEGIN':
            self.process_challenge_request()
        elif message == 'CHALLENGE_START':
            self.process_challenge_start_request()
        else:
            super(ManagerConnection, self).check_message(message)
            
    def process_challenge_request(self):
        if self.boss.challenge_active:
            print('Boss rejects challenge request')
            self.write_line('CHALLENGE_REJECTED')
            return
        
        self.write_line('CHALLENGE_ACCEPTED')
        # receive challenge id, challenge name, number of lines in descirption, 
        # description, and tarred file
        challenge_id = self.read_line()
        print(challenge_id)
        challenge_name = self.read_line()
        print(challenge_name)
        description_line_count = int(self.read_line())
        print(description_line_count)
        
        description = ''
        for i in range(description_line_count):
            line = self.read_line()
            description = ''.join([description, line+"\n"])
            
        # begin file transmission
        message = self.read_line()
        if message != 'FILE_TRANSMISSION_BEGIN':
            print('Expected file transmission begin message, '
                + 'but got {} instead.'.format(message))
            return
        
        # grab the lines
        files = self.read_files()
        
        print('files received')
        # create the challenge object with all of the information and data
        new_challenge = challenge.Challenge(challenge_id, challenge_name,
            description, files)
        self.boss.challenge = new_challenge
        print('boss equipped with challenge')
            
        # everything went well, so send OK to manager
        self.write_line('CHALLENGE_OKAY')
        print('left this place')
    
    def process_challenge_start_request(self):
        """ """
        if not self.boss.challenge:
            self.write_line('CHALLENGE_NOT_FOUND')
            return
        
        elif not self.boss.run_challenge():
            self.write_line('CHALLENGE_START_ERROR')
            return
        
        self.boss.challenge_active = True
        
    def run(self):
        """ """
        self.write_line("CONNECTION_ACCEPTED")
        super(ManagerConnection, self).run()
    
    def close(self):
        super(ManagerConnection, self).close()
        # remove from boss
        delattr(self.boss, 'manager')
