import os
import time
import signal
import difflib
import threading
import socketserver

# Keep track of how much time has elapsed
START = -1

class ThreadedSubmissionRequestHandler(socketserver.StreamRequestHandler):
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

class ThreadedSubmissionServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == '__main__':
    host, port = 'localhost', 9999

    # Create the server, binding to localhost on port 9999
    server = ThreadedSubmissionServer((host, port), ThreadedSubmissionRequestHandler)
    # Start a thread with the server -- that thread will then start one more
    # thread for each request
    server_thread = threading.Thread(target=server.serve_forever)

    def signal_handler(signal, frame):
        print(' Tearing down the server...')
        server.shutdown()
        os._exit(0)

    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    # Start the global timer
    START = time.time()
    # Serve it up
    server_thread.start()

    while True:
        try: 
            time.sleep(1)
            continue
        except:
            pass
