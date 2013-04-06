import threading

class Client(threading.Thread):
    """
    Abstract client class: used to impement all types of connecting
    clients to the Server.
    
    """
    def __init__(self, socket):
        """Keeps track of the socket and the file posing as the socket"""
        threading.Thread.__init__(self)
        self.socket = socket
        self.stream = socket.makefile()
        self.active = True
    
    def read_line(self):
        """Returns a line read from the socket."""
        return self.stream.readline().strip()
    
    def write_line(self, message):
        """Writes a message (line) to the socket"""
        self.socket.send(bytes(message + "\n", 'utf-8'))
    
    def check_message(self, message):
        """ """
        if message == "x":
            self.active = False
    
    def run(self):
        """ """
        while self.active:
            self.check_message(self.read_line())
        self.close()
    
    def close(self):
        """Closes the socket and the file"""
        self.write_line("CLOSE_CONNECTION")
        self.stream.close()
        self.socket.close()
