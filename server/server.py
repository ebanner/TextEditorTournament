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
        # Get the magic character sequence to end communication
        self.magic = str(self.rfile.readline().strip(), 'utf-8')
        print('Magic chars:', self.magic)
        self.file = str(self.rfile.readline().strip(), 'utf-8')
        print('Name of file: {}'.format(self.file))
        self.participant = str(self.rfile.readline().strip(), 'utf-8')
        print('Participant: {}'.format(self.participant))

        # Read in the blank line
        self.data = self.rfile.readline()
        submission_lines = []

        while True:
            self.data = str(self.rfile.readline(), 'utf-8')

            if self.data.strip() == self.magic:
                # End of the user's submission file
                break
            else:
                submission_lines.append(self.data)

        # Open up the correct file and diff it with the submission
        with open(self.file+'.sol', 'r') as f:
            correct_lines = f.readlines()

            with open(self.file+'.log', 'a') as g:
                # Log the participant
                g.write(self.participant + "\n")

                for line in difflib.unified_diff(submission_lines, correct_lines,
                        fromfile=self.file, tofile=self.file+'.sol'):
                    self.wfile.write(bytes(line, 'utf-8'))
                    # Log the participant's diff
                    g.write(line)

                # Log the participant's time
                g.write(str(time.time() - START) + "\n")

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
