import difflib
import socketserver

class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # Get the magic character sequence to end communication
        magic = str(self.rfile.readline().strip(), 'utf-8')
        print('Magic chars:', magic)
        self.data = str(self.rfile.readline().strip(), 'utf-8')
        print('Participant: {}'.format(self.data))
        self.data = str(self.rfile.readline().strip(), 'utf-8')
        print('Name of file: {}'.format(self.data))

        # Read in the blank line
        self.data = self.rfile.readline()
        submission_lines = []

        while True:
            self.data = str(self.rfile.readline(), 'utf-8')

            if self.data.strip() == magic:
                # End of the user's submission
                break
            else:
                submission_lines.append(self.data)

        # Open up the correct file and diff it with the submission
        with open('foo.txt', 'r') as f:
            correct_lines = f.readlines()

            for line in difflib.unified_diff(submission_lines, correct_lines,
                    fromfile='foo.txt', tofile='bar.txt'):
                self.wfile.write(bytes(line, 'utf-8'))

        # Send the terminating character sequence to the client
        self.wfile.write(bytes(magic, 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
