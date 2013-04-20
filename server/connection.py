import threading
import file_obj


class Connection(threading.Thread):
    """
    Abstract client class: used to impement all types of connecting
    clients to the Server.
    
    """
    def __init__(self, socket, boss=None):
        """Keeps track of the socket and the file posing as the socket"""
        threading.Thread.__init__(self)
        self.socket = socket
        self.stream = socket.makefile()
        self.boss = boss
        self.active = True
        self.closed = False
    
    def read_line(self):
        """Returns a line read from the socket."""
        line = self.stream.readline().strip()
        print('READ: {}'.format(line))
        return line
        
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
        print('WRITE: {}'.format(message))
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

    def init_challenge(self, challenge):
        """Send challenge information to each client."""
        self.write_line('CHALLENGE_INITIATE')
        self.write_line(str(challenge.id))
        print('Sent id')
        self.write_line(challenge.name)
        print('Sent name')
        self.write_line(str(len(challenge.description)))
        print('Sent # of lines = {}'.format(len(challenge.description)))
        for line in challenge.description:
            print(line)
            self.write_line(line)
        print('Sent description (line by line)')

    def send_participant_accept_message(self, name, editor):
        """Sends a message saying that a participant accepted a challenge."""
        self.write_line('PARTICIPANT_ACCEPTED')
        self.write_line(name)
        self.write_line(editor)

    def send_challenge_ready(self, n_part_accepting, n_part_total):
        """
        Sends a message indicating that all participants have responded in
        accepting or rejecting a challenge, and how many of a total number of
        participants have chosen to accept the challenge.
        """
        print('IN SEND_CHALLENGE_READY')
        self.write_line('PARTICIPANT_LIST_FINISHED')
        self.write_line(str(n_part_accepting))
        self.write_line(str(n_part_total))
    
