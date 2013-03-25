import random
import socket
import sys

def send_file(socket, filename):
    """Sends a file to socket"""
    with open(filename, 'rb') as f, open('info.txt', 'r') as g:
        # Information about the participant
        name, editor = g.readlines()
        # Send name and editor to the submission server
        socket.sendall(bytes(name, 'utf-8'))
        socket.sendall(bytes(editor, 'utf-8'))
        # Send the name of the file being submitted
        socket.sendall(bytes(filename + "\n", 'utf-8'))
        # Get the participant's file
        data = f.read()
        # Send the size of the submission file to the submission server
        socket.sendall(bytes(str(f.tell()) + "\n", 'utf-8'))
        # Send the file itself
        socket.sendall(data)

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

    finally:
        sock.close()
