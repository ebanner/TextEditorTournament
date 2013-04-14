import threading
import file_obj


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
        self.closed = False
    
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
            new_file = file_obj.File(file_name, file_lines)
            files.append(new_file)
            
        return files
    
    def write_files(self, file_list):
        """
        Writes the files out to the socket, line by line, file by file.
        The list of files provided should be a list of file_obj.py File
        objects (customized file object, not actual filesystem files).
            - receive "FILE_TRANSMISSION_BEGIN"
            - while "SEND_FILE_BEGIN", do:
                - receive file name
                - receive number of lines (n)
                - for each line (i<n), receive line
                    - write file into working directory
            - receive "FILE_TRANMISSION_END"
        """
        self.write_line('FILE_TRANSMISSION_BEGIN')
        
        for f in file_list:
            self.write_line('SEND_FILE_BEGIN')
            self.write_line(f.name)
            self.write_line(str(len(f.lines)))
            for line in f.lines:
                self.write_line(line)
            
        self.write_line('FILE_TRANMISSION_END')
    
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
        self.closed = True
