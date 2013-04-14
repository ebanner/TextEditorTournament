#!/usr/bin/python3

# participant submit client
import socket
import sys
import os
import glob


HOST = 'localhost'
PORT = 9999
WORKING_DIRECTORY = 'battlefield'

class File:
    """Keeps track of the name of the file and every line"""
    def __init__(self, name, lines):
        self.name = name
        self.lines = lines
        # test print lines
        for line in lines:
            print(line)

class Client():
    """
    
    """
    def __init__(self, socket):
        """Keeps track of the socket and the file posing as the socket"""
        self.socket = socket
        self.stream = socket.makefile()
        self.active = True
        self.editor = 'Emacs'
        self.name = 'Richard Stallman'
    
    def read_line(self):
        """Returns a line read from the socket."""
        return self.stream.readline().strip()
    
    def write_line(self, message):
        """Writes a message (line) to the socket"""
        self.socket.sendall(bytes(message + "\n", 'utf-8'))
    
    def read_files(self):
        """Reads files from input until FILE_TRANMISSION_END received"""
        files = []
        while True:
            msg = self.read_line()
            if msg != 'SEND_FILE_BEGIN':
                break
            file_name = self.read_line()
            print("NEW FILE:")
            print(file_name)
            num_lines = int(self.read_line())
            file_lines = []
            for i in range(num_lines):
                file_lines.append(self.read_line())
            new_file = file_obj.File(file_name, file_lines)
            files.append(new_file)
            
        return files
    
    def check_message(self, message):
        """ """
        if message == "CHALLENGE_INITIATE":
            self.init_challenge()
        if message == "CONNECTION_CLOSED":
            self.active = False
            
    def init_challenge(self):
        """
        receive challenge number (id)
        receive challenge name
        receive number of lines in description (n)
        receive challenge description (n lines)
        """
        # get challenge info
        challenge_id = self.read_line()
        print(challenge_id)
        challenge_name = self.read_line()
        print(challenge_name)
        description_line_count = int(self.read_line())
        
        description = ''
        for i in range(description_line_count):
            description = ''.join([description, self.read_line()])
        print(description)
        
        #prompt user to accept or reject
        print('Would you like to accept this challenge? [Y/n]')
        answer = input(' > ')
        if answer.lower() == 'y':
            self.write_line('CHALLENGE_ACCEPTED')
            self.accept_challenge()
        else:
            self.write_line('CHALLENGE_REJECTED')
        
    def accept_challenge(self):
        """Retrieve the challenge files from the Boss.
        
        Receive the files.
        (1)
        Wait until user wants to submit.
        Submit.
        Receive diff (if any).
        GOTO (1)
        
        """
        print('IN accept_challege()')
        message = self.read_line()
        if message == 'CHALLENGE_CANCELLED':
            print('The challenge was CANCELLED by your administrator.')
            return
        elif message != 'FILE_TRANSMISSION_BEGIN':
            print("Didn't get the go-ahead for file transmission.")
            return
        
        files = self.read_files()
        
        # wipe all of the files in the working directory
        for file_name in glob.glob("*"):
            os.remove(file_name)
            
        for start_file in files:
            with open(start_file.name, 'w') as f:
                # write every line to the file with a newline
                f.write(''.join([ line + "\n" for line in start_file.lines ]))
        
        forfeit_string = "{} is the worst editor".format(self.editor)
        print('Press ENTER to submit your work or "{} to '
            'forfeit.'.format(forfeit_string))
        finished = False
        while not finished:
            key = input(' > ')
            if key == forfeit_string:
                self.write_line('CHALLENGE_FORFEIT')
                finished = True
            # TODO: elif key == "challenge reset"
            else:
                if not self.submit_for_review(challenge_id):
                    print('Failed to send all files for review')
                    continue
                else:
                    feedback = self.read_line()
                    if feedback == "CHALLENGE_RESULTS_INCORRECT":
                        continue
                    else:
                        print('Congrats! Well done.')
                        finished = True
                
        
    def submit_for_review(self, challenge_id):
        """Read all of the submission files into memory and send them to the 
        pariticpant connection server for grading."""
        # read files into a list
        files = []
        for file_name in glob.glob("*"):
            try:
                with open(file_name, 'r') as f:
                    next_file = File(file_name,
                        [ line.strip() for line in f.readlines() ])
            except IOError:
                print("Couldn't create the list of files "
                "{}".format(WORKING_DIRECTORY))
                return False
            
            files.append(next_file)
            print('{} added to the list.'.format(file_name))
            
        # send files to server for grading
        self.write_line('CHALLENGE_SUBMISSION')
        self.write_line(challenge_id)
        print('writing files')
        self.write_line('FILE_TRANSMISSION_BEGIN')
        for f in files:
            self.write_line('SEND_FILE_BEGIN')
            self.write_line(f.name)
            self.write_line(str(len(f.lines)))
            for line in f.lines:
                self.write_line(line)
        self.write_line('FILE_TRANMISSION_END')
        
        print('finished writing files')
        return True
    
    def close(self):
        """Closes the socket and the file"""
        # self.write_line("CONNECTION_CLOSED")
        self.stream.close()
        self.socket.close()
    
    def run(self):
        """Main loop - body of the program"""
        
        self.write_line("TEXT_EDITOR_TOURNAMENT_TYPE_PARTICIPANT")
        
        response = self.read_line()
        if response != 'CONNECTION_ACCEPTED':
            print(response)
            return
        print(response)
        
        # get user name and editor and send this info
        self.user = input("Name:   ")
        self.editor = input("Editor: ")
        self.write_line(self.user)
        self.write_line(self.editor)
        print("user and editor info sent, waiting in main loop")
        
        # enter main loop
        while self.active:
            self.check_message(self.read_line())


if __name__ == '__main__':
    if len(sys.argv) > 2:
        ignored_filename, HOST, PORT = sys.argv
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, int(PORT)))
    except Exception as e:
        print(e)
        print('Something went wrong with connecting to the server. I quit.')
        exit()
    
    # create the working directory and cd into it
    if not os.path.exists(WORKING_DIRECTORY):
        os.makedirs(WORKING_DIRECTORY)
    os.chdir(WORKING_DIRECTORY)
    
    client = Client(sock)
    client.run()
    client.close()
