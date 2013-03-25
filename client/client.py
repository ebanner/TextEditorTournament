import random
import socket
import sys

CACHED_PACKET = ''
MAGIC = '{:x}'.format(random.getrandbits(128))

def send_file(socket, filename):
    """Sends a file to socket"""
    # Send the magic character sequence that signifies the end of
    # communication.
    socket.sendall(bytes(MAGIC + "\n", 'utf-8'))
    # Send the name of the file being submitted
    socket.sendall(bytes(filename + "\n", 'utf-8'))

    # Send the entire file to the submission server
    with open(filename, 'rb') as f:
        data = f.read()
        socket.sendall(data)

    # Send the magic char sequence indicating we are done sending the file
    socket.sendall(bytes(MAGIC + "\n", 'utf-8'))

def receive_diff(socket):
    """Get the diff back from the server"""
    diff = ''

    # Receive the diff from the server
    for line in socket.makefile():
        diff = ''.join([diff, line])

    return diff

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = 'foo.txt'

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(('localhost', 9999))
        # Submit the file to the server for grading
        send_file(sock, filename)
        # Get the diff back from the submission server
        diff = receive_diff(sock)

        # Print out the diff if the user submitted an incorrect answer
        if diff:
            print("Incorrect repsonse. Here's the diff:\n")
            print(diff, end='')
        else:
            print('You got it right!')
            print(diff)

    finally:
        sock.close()
