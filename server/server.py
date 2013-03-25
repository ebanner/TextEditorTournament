import time
import difflib
import socketserver

# Keep track of how much time has elapsed
START = 0

class SubmissionServer(socketserver.StreamRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # Name of the participant
        self.participant = str(self.rfile.readline().strip(), 'utf-8')
        print('Participant: {}'.format(self.participant))
        # Participant's editor
        self.editor = str(self.rfile.readline().strip(), 'utf-8')
        print('Editor: {}'.format(self.editor))
        # Name of the submission file
        self.file = str(self.rfile.readline().strip(), 'utf-8')
        print('Name of file: {}'.format(self.file))
        # Number of bytes in the entire file
        self.length = int(self.rfile.readline().strip())
        print('Number of bytes: {}'.format(self.length))

        # Read in the entire body and convert it to a string
        self.body = self.rfile.read(self.length).decode('utf-8').split("\n")
        self.submission_lines = [ ''.join([line, "\n"]) for line in self.body ]
        self.submission_lines.pop()

        # Open up the correct file and diff it with the submission
        with open(self.file+'.sol', 'r') as sol, open(self.file+'.log', 'a') as log: 
            correct_lines = sol.readlines()

            # Log the participant and his or her editor
            log.write(self.participant + "\n")
            log.write(self.editor + "\n")

            for line in difflib.unified_diff(self.submission_lines, correct_lines,
                    fromfile=self.file, tofile=self.file+'.sol'):
                self.wfile.write(bytes(line, 'utf-8'))
                # Log the participant's diff
                log.write(line)

            # Log the participant's time
            log.write(str(time.time() - START) + "\n\n")

        # Print time elapsed
        end = time.time()
        print(end - START)

if __name__ == "__main__":
    host, port = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((host, port), SubmissionServer)

    # Start the timer!
    START = time.time()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
