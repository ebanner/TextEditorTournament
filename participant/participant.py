#!/usr/bin/python3

# participant submit client
import socket
import sys
import os
import glob
import file_obj


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
    """A client-side participant.

    This class emboides a participant in the text-editor tournament. Most of the
    time, this class is waiting for the server to send it a challenge to it can
    either accept or reject. Once accepted, the participant waits for the
    challenge to kick off. Once it does, the blocking behavior shifts from
    waiting on a socket connected to the server to waiting for the user to type
    `submit' at STDIN.

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
        """Check to see what type of activity the server wants to engage the
        participant in.

        Currently, the only type of activity the server would want with the
        participant is to send the participant an invitation for a challenge.
        
        """
        if message == "CHALLENGE_INITIATE":
            self.init_challenge()
        elif message == "CONNECTION_CLOSED":
            self.active = False
        elif message == 'CHALLENGE_START':
            self.process_challenge_start()
        elif message == 'CHALLENGE_CANCELLED':
            self.process_challenge_cancelled()
            
    def process_challenge_cancelled(self):
        print('The challenge was CANCELLED by your administrator. That is all.')

    def init_challenge(self):
        """Receive challenge information from the server and either accept or
        reject the challenge."""
        # Get challenge info
        challenge_id = self.read_line()
        print('Challenge ID: {}'.format(challenge_id))
        challenge_name = self.read_line()
        print('Challenge Name: {}'.format(challenge_name))
        description_line_count = int(self.read_line())
        
        # Print out the description
        description = ''
        for i in range(description_line_count):
            line = self.read_line()
            description = ''.join([description, line+"\n"])
        print('Description: {}'.format(description))
        
        # Prompt user to accept or reject
        print('Would you like to accept this challenge? [Y/n]')
        answer = input(' > ')
        if answer.lower() == 'y':
            self.write_line('CHALLENGE_ACCEPTED')
        else:
            self.write_line('CHALLENGE_REJECTED')
        
    def process_challenge_start(self):
        """Retrieve the challenge files from the Boss.
        
        Receive the files.
        (1)
        Wait until user wants to submit.
        Submit.
        Receive diff (if any).
        GOTO (1)
        
        """
        print('IN process_challenge_start()')

        message = self.read_line()
        assert message == 'FILE_TRANSMISSION_BEGIN'
        files = self.read_files()
        
        # Wipe all of the files in the working directory
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
        participant connection server for grading."""
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
        
        # Get user name and editor and send this info
        self.user = input("Name:   ")
        self.editor = input("Editor: ")
        self.write_line(self.user)
        self.write_line(self.editor)
        print("user and editor info sent, waiting in main loop")
        
        # Enter main loop
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
    
    # Create the working directory and cd into it
    if not os.path.exists(WORKING_DIRECTORY):
        os.makedirs(WORKING_DIRECTORY)
    os.chdir(WORKING_DIRECTORY)
    
    client = Client(sock)
    client.run()
    client.close()
