import socketserver

class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
      # self.rfile is a file-like object created by the handler;
      # we can now use e.g. readline() instead of raw recv() calls
      self.data = self.rfile.readline()
      print('Name: {}'.format(self.data))

      # Read in the blank line
      self.data = self.rfile.readline()

      with open('bar.txt', 'wb') as f:
        while True:
          self.data = self.rfile.readline()

          # End of the user's submission
          if str(self.data.strip(), 'utf-8') == 'XXX':
            break
          else:
            f.write(self.data)
            self.wfile.write(self.data)

      # Send the terminating character sequence to the client
      self.wfile.write(bytes('XXX', 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
