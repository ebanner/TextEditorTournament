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
        # Get the name of the participant
        self.participant = str(self.rfile.readline().strip(), 'utf-8')
        print('Participant: {}'.format(self.participant))
        # Get the participant's editor
        self.editor = str(self.rfile.readline().strip(), 'utf-8')
        print('Editor: {}'.format(self.editor))
        # Get the name of the submission file
        self.file = str(self.rfile.readline().strip(), 'utf-8')
        print('Name of file: {}'.format(self.file))
        # Get the number of bytes remaining in the file
        self.length = int(self.rfile.readline().strip())
        print('Number of bytes: {}'.format(self.length))

        # Read in the entire body and convert it to a string
        self.body = self.rfile.read(self.length).decode('utf-8').split("\n")
        self.submission_lines = [ ''.join([line, "\n"]) for line in self.body ]
        # Annoying non-existant line returned by split
        self.submission_lines.pop()

        # Open up the correct file and diff it with the submission
        with open(self.file+'.sol', 'r') as f:
            correct_lines = f.readlines()

            with open(self.file+'.log', 'a') as g:
                # Log the participant
                g.write(self.participant + "\n")

                for line in difflib.unified_diff(self.submission_lines, correct_lines,
                        fromfile=self.file, tofile=self.file+'.sol'):
                    self.wfile.write(bytes(line, 'utf-8'))
                    # Log the participant's diff
                    g.write(line)

                # Log the participant's time
                g.write(str(time.time() - START) + "\n\n")

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
