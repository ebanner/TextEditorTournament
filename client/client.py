#!/usr/bin/python3

import os
import sys
import random
import socket

def send_file(socket, filename):
    """Sends a file to the submission server to be judged.
    
    Submissions are transferred as follows:

      The name of the participant followed by a newline.
      The name of the participant's editor followed by a newline.
      The name of the file being submitted by the participant followed by a newline.
      The size of the submission file in bytes.
      The file itself.

    A typical example:

      Richard Stallman\n
      GNU Emacs\n
      .emacs
      109
      My claim to fame is having written the slowest, and the most egregiously
      bloated text editor of all time.

    """
    try:
        # Send the metadata stored in `info.txt' along with the submission file
        # to the submission server for judging.
        with open(filename, 'rb') as sub, open('info.txt', 'r') as info:
            data = sub.read()
            name, editor = info.readlines()
            socket.sendall(bytes(name, 'utf-8'))
            socket.sendall(bytes(editor, 'utf-8'))
            socket.sendall(bytes(filename + "\n", 'utf-8'))
            socket.sendall(bytes(str(sub.tell()) + "\n", 'utf-8'))
            socket.sendall(data)

    except FileNotFoundError as e:
        print(e)
        os._exit(1)

def receive_diff(socket):
    """Get the diff back from the submission server"""
    diff = ''

    # Build the diff from the submission server line by line
    for line in socket.makefile():
        diff = ''.join([diff, line])

    return diff

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = 'foo.txt'

    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', 9999))
        send_file(sock, filename)
        diff = receive_diff(sock)

        # Print out the diff if the user submitted an incorrect answer
        if diff:
            print("Incorrect repsonse. Here's the diff:\n")
            print(diff, end='')
        else:
            print('You got it right!')
