# manager client
import socket
import sys


HOST = 'localhost'
PORT = 9999

class Client():
    """
    
    """
    def __init__(self, socket):
        """Keeps track of the socket and the file posing as the socket"""
        self.socket = socket
        self.stream = socket.makefile()
        self.active = True
        self.commands = {
            'start' : self.start_challenge,
            'send' : self.send_challenge,
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
        print("send command")
        
    def start_challenge(self, ignored):
        print("start command")
    
    def quit(self, ignored):
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
    
    client = Client(sock)
    client.run()
    client.close()
