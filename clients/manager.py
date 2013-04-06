#!/usr/bin/python3

import socket
import sys
import os
import tarfile
import glob

HOST = 'localhost'
PORT = 9999

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
            'start' : self.start_challenge,
            'send' : self.send_challenge,
            'ls' : self.list_challenges,
            'exit' : self.quit,
            'quit' : self.quit
        }
    
    def read_line(self):
        """Returns a line read from the socket."""
        return self.stream.readline().strip()
    
    def write_line(self, message):
        """Writes a message (line) to the socket"""
        self.socket.sendall(bytes(message + "\n", 'utf-8'))
    
    def check_message(self, message):
        """ """
        if message == "CONNECTION_CLOSED":
            self.active = False
    
    def close(self):
        """Closes the socket and the file"""
        # self.write_line("CONNECTION_CLOSED")
        self.stream.close()
        self.socket.close()
    
    def next_command(self):
        """ """
        cmd = input(" > ")
        verb, space, rest = cmd.partition(' ')
        if verb in self.commands:
            self.commands[verb](rest)
        else:
            print("wat??? (unknown command)")
        
    def run(self):
        """Main loop - body of the program"""
        
        self.write_line("TEXT_EDITOR_TOURNAMENT_TYPE_MANAGER")
        
        response = self.read_line()
        if response != 'CONNECTION_ACCEPTED':
            print(response)
            return
        print(response)
        
        while self.active:
            self.next_command()
        
    def send_challenge(self, parameters):
        """
        parameters: "challenge_id challenge_name"
        """
        parameters = parameters.split(' ')
        if len(parameters) != 2:
            print('Expecting challenge_id challenge_name')
        elif not os.path.isdir(parameters[1]):
            print('{} directory does not exist'.format(parameters[1]))
        else:
            challenge = parameters[1]
            os.chdir(challenge)
            try:
                tar = tarfile.open(challenge+'.tar', "w")
                for file_name in glob.glob("*"):
                    if file_name == 'description.info' or file_name.endswith('.tar'):
                        continue
                    tar.add(file_name)
                    print('{} added to the tar.'.format(file_name))
            except IOError:
                print("Couldn't create the tar {}".format(challenge))
            finally:
                tar.close()
                
            # read description file
            try:
                with open('description.info', 'r') as f:
                    challenge_name = f.readline().strip()
                    # ignore empty line
                    f.readline() 
                    description = [ line.strip() for line in f.readlines() ]
            except IOError as e:
                print('Unable to open description file {}'.format(e))
                return
                
            if not challenge_name or not description:
                # empty challenge name or description
                print('Empty challenge name or description')
                print('Challenge name: {}'.format(challenge_name))
                print('Description: {}'.format(description))
                return
            
            print("Starting send...")
            # successfully created the tar and read in desciption file. Now send 
            # challenge information to server.
            self.write_line('CHALLENGE_SEND_BEGIN')
            response = self.read_line()
            print(response)
            if response != 'CHALLENGE_ACCEPTED':
                print('Challenge rejected by server')
                return
            
            # send challenge id, challenge title, and other things
            challenge_id = parameters[0]
            self.write_line(challenge_id)
            self.write_line(challenge_name)
            self.write_line(str(len(description)))
            for line in description:
                self.write_line(line)
            
            print('waiting to send the tar now')
        
    def start_challenge(self, ignored):
        """ """
        print("start command")
    
    def list_challenges(self, ignored):
        """ """
        for root, dirs, files in os.walk(".", topdown=False):
            if dirs:
                print(dirs[0])
    
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
