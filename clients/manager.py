#!/usr/bin/python3

import socket
import sys
import os
import tarfile
import glob

HOST = 'localhost'
PORT = 9999

class File:
    """A struct that contains the name of a file and the lines in the file"""
    def __init__(self, name, lines):
        self.name = name
        self.lines = lines

class Manager():
    """
    The Manager is a client that listens for user commands through standard
    input and sends them to the Text Editor Challenge server. It is responsible
    for sending challenge information and files to the server, and for giving
    the server instructions on when to distribute the challenge to all
    participants.
    
    """
    def __init__(self, socket):
        """
        Keeps track of the socket and the file posing as the socket, and
        defines a commands-function dictionary to parse user input.
        """
        self.socket = socket
        self.stream = socket.makefile()
        self.active = True
        self.commands = {
            'load' : self.send_challenge,
            'send' : self.send_challenge, # deprecated
            'submit' : self.send_challenge,
            'init' : self.init_challenge,
            'ls' : self.list_challenges,
            'exit' : self.quit,
            'quit' : self.quit
        }
        self.challenge_loaded = False
    
    def read_line(self):
        """Returns a line read from the socket."""
        return self.stream.readline().strip()
    
    def write_line(self, message):
        """Writes a message (line) to the socket"""
        self.socket.sendall(bytes(message + "\n", 'utf-8'))
        
    def write(self, data):
        """Writes data to the socket"""
        self.socket.sendall(data)
    
    def close(self):
        """Closes the socket and the file"""
        #self.write_line("CONNECTION_CLOSED")
        self.stream.close()
        self.socket.close()
    
    def next_command(self):
        """Reads a command from STDIN and processes it.
        
        Most of the life of a manager is spent reading from STDIN, waiting for
        the user to issue a command. Valid commands are as follows:

        <[load] [send] [submit]> <challenge_id> <challenge_name>
            Load a challenge into memory. A brief description of the arguments
            follow:
            
                challenge_id an identifier that serves to uniquely identify
                a challenge (an integer will usually suffice).

                challenge_name is the name of the challenge to be loaded.
                This challenge name must exist as a directory in the
                current directory and contains the following files:

                    '*.sol' files that serve as the solution files for the
                    current challenge

                    A `description.info' file that contains the information
                    for the current challenge (the challenge title followed
                    by a newline followed by the description).

                    Every other file is a file that is to be distributed to
                    the participant.

        <init>
            Assuming a challenge has been loaded into memory, begin the
            challenge. This results in the boss server sending out the challenge
            files to each of the participants.
        
        <ls>
            List the challenges in the current directory.

        <[quit] [exit]>
            Exit the manager program.

        """
        cmd = input(" > ")
        verb, space, rest = cmd.partition(' ')
        if verb in self.commands:
            self.commands[verb](rest)
        else:
            print("wat??? (unknown command)")
        
    def run(self):
        """Identify yourself as a manager and read commands from STDIN.

        Most of the life of a manager is spent in this function.

        """
        self.write_line("TEXT_EDITOR_TOURNAMENT_TYPE_MANAGER")
        
        response = self.read_line()
        if response != 'CONNECTION_ACCEPTED':
            print(response)
            return
        print(response)
        
        while self.active:
            self.next_command()
        
    def send_challenge(self, parameters):
        """Load a challenge into memory.

        This function must be invoked prior to beginning a challenge. The
        `parameters' argument is a whitespace-separated string of two words. The
        first word is the challenge id. The second word is the challenge name.
        The challenge name must be a directory that exists in the current
        directory.
        
        """
        parameters = parameters.split(' ')
        if len(parameters) != 2:
            print('Expecting challenge_id challenge_name')
            return
        elif not os.path.isdir(parameters[1]):
            print('{} directory does not exist'.format(parameters[1]))
            return

        # Read files into a list
        challenge_dir = parameters[1]
        # cd into the challenge directory
        os.chdir(challenge_dir)
        files = []
        for file_name in glob.glob('*'):
            if file_name == 'description.info':
                continue
            try:
                with open(file_name, 'r') as f:
                    next_file = File(file_name,
                        [ line.strip() for line in f.readlines() ])
            except IOError:
                print("Couldn't create the list of files {}".format(challenge_dir))
                # cd back to previous directory
                os.chdir(os.pardir)
                return
            
            # Add the file to the list of challenge files
            files.append(next_file)
            print('{} added to the list.'.format(file_name))
        
        # Read description file
        try:
            with open('description.info', 'r') as f:
                challenge_name = f.readline().strip()
                f.readline() # ignore empty line
                description = [ line.strip() for line in f.readlines() ]
        except IOError as e:
            print('Unable to open description file {}'.format(e))
            return
        finally:
            # Go back to original directory
            os.chdir(os.pardir)
            
        if not challenge_name or not description:
            # Empty challenge name or description
            print('Empty challenge name or description')
            print('Challenge name: {}'.format(challenge_name))
            print('Description: {}'.format(description))
            return
        
        print("Starting send...")
        self.write_line('CHALLENGE_SEND_BEGIN')
        response = self.read_line()
        print(response)
        if response != 'CHALLENGE_ACCEPTED':
            print('Challenge rejected by server')
            return
        
        # Send challenge id, challenge name, length of the description, and
        # the description itself
        challenge_id = parameters[0]
        self.write_line(challenge_id)
        self.write_line(challenge_name)
        self.write_line(str(len(description)))
        for line in description:
            self.write_line(line)
        
        # Send the files one by one
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
        response = self.read_line()
        if response != 'CHALLENGE_OKAY':
            print('Challenge not accepted by Boss')
            return
        
        print(response)
        self.challenge_loaded = True
    
    def init_challenge(self, ignored):
        """Inform the server to send challenge description to each participant
        and wait for replies from participants."""
        if not self.challenge_loaded:
            print('You must first send a challenge to the server.')
            return

        self.write_line('CHALLENGE_INITIATE')
        response = self.read_line()
        if response != 'PARTICIPANT_ACCEPTED':
            print('Challenge rejected by server:')
            if response == 'CHALLENGE_NOT_FOUND':
                print('   No challenge has been sent to the server yet.')
            elif response == 'CHALLENGE_ALREADY_ACTIVE':
                print('   Another challenge is already active.')
            elif response == 'NO_PARTICIPANTS_CONNECTED':
                print('   There are no participants connected to the server.')
            else:
                print('   Unknown error.')
            return
        
        while response != 'PARTICIPANT_LIST_FINISHED':
            participant_name = self.read_line()
            participant_editor = self.read_line()
            print('Participant "{}" accepted the challenge (editor "{}").'
                .format(participant_name, participant_editor))
            response = self.read_line()
        
        num_participants_accepting = self.read_line()
        num_participants_total = self.read_line()
        print('{} of {} participants accepted challenge. '
        'Type start to begin'.format(num_participants_accepting,
            num_participants_total))
        
        print('Would you like to start the challenge? [Y/n]')
        answer = input(' > ')
        if answer.lower() != 'y':
            self.write_line('CHALLENGE_CANCEL')
            return
        
        self.write_line('CHALLENGE_START')
        response = self.read_line()
        if response == 'CHALLENGE_FINISH':
            print('Challenge successfully completed.')
        else:
            print('There was a problem with the challenge.')
        
    def list_challenges(self, ignored):
        """List all of the challenges available.
        
        Every challenge must be a directory in the current directory.
        
        """
        file_list = []
        for root, dirs, files in os.walk(".", topdown=False):
            if dirs:
                file_list = dirs
                break
        print(', '.join(map(str, file_list)))
    
    def quit(self, ignored):
        """Quit the program."""
        self.active = False


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
    
    mngr = Manager(sock)
    mngr.run()
    mngr.close()
