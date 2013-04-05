# server library
import socketserver

# application imports
import boss


# global variables
HOST, PORT = "localhost", 9999
boss = boss.Boss()


class MyTCPHandler(socketserver.StreamRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    
    """
    def handle(self):
        # differentiate type of client and accept/reject
        self.connection_type = str(self.rfile.readline().strip(), 'utf-8')
        print(self.connection_type)
        if self.connection_type == 'TEXT_EDITOR_TOURNAMENT_TYPE_PARTICIPANT':
            boss.add_client(self)
        else:
            print('Rejected')


if __name__ == "__main__":
    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
