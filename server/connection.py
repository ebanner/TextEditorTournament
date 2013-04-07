import threading


class File:
    """
    
    """
    def __init__(self, name, lines):
        self.name = name
        self.lines = lines
        # test print lines
        for line in lines:
            print(line)


class Connection(threading.Thread):
    """
    Abstract client class: used to impement all types of connecting
    clients to the Server.
    
    """
    def __init__(self, socket, boss):
        """Keeps track of the socket and the file posing as the socket"""
        threading.Thread.__init__(self)
        self.socket = socket
        self.stream = socket.makefile()
        self.boss = boss
        self.active = True
    
    def read_line(self):
        """Returns a line read from the socket."""
        return self.stream.readline().strip()
        
    def read(self, num_bytes):
        return bytes(self.stream.read(num_bytes), 'utf-8')
    
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
            new_file = File(file_name, file_lines)
            files.append(new_file)
        return files
    
    def write_line(self, message):
        """Writes a message (line) to the socket"""
        self.socket.sendall(bytes(message + "\n", 'utf-8'))
    
    def check_message(self, message):
        """ """
        if not message or message == "CONNECTION_CLOSED":
            self.active = False
    
    def run(self):
        """ """
        while self.active:
            self.check_message(self.read_line())
        self.close()
    
    def close(self):
        """Closes the socket and the file"""
        self.write_line("CONNECTION_CLOSED")
        self.stream.close()
        self.socket.close()
