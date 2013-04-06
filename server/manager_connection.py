# manager.py
import connection

class ManagerConnection(connection.Connection):
    """
    tbd
    
    """
    def check_message(self, message):
        """ """
        print(message)
        if message == 'CHALLENGE_SEND_BEGIN':
            self.process_challenge_request()
        else:
            super(ManagerConnection, self).check_message(message)
            
    def process_challenge_request(self):
        if self.boss.active_challenge:
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
            
        # receive the number of bytes in the tarred file and the tarred file
        tar_data_length = int(self.read_line())
        tar_data = self.read(tar_data_length)
        try:
            with open('sample.tar', 'wb') as tar:
                tar.write(tar_data)
        except IOError:
            print('Could not write the tar file to disk.')
            self.write_line('SERVER_ERROR')
            return
        
        self.write_line('CHALLENGE_OKAY')
        print(self.read_line())
        print(description)          
        
    def run(self):
        """ """
        self.write_line("CONNECTION_ACCEPTED")
        super(ManagerConnection, self).run()
    
    def close(self):
        super(ManagerConnection, self).close()
        # remove from boss
        delattr(self.boss, 'manager')
