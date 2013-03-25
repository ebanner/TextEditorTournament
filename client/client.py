#!/usr/bin/python3

import os
import sys
import random
import socket

def send_file(socket, filename):
    """Sends a file to the submission server to be judged"""
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
    if len(sys.argv) == 4:
        script, filename, host, port = sys.argv
    elif len(sys.argv) == 2:
        script, filename = sys.argv
        host, port = 'localhost', 9999
    else:
        print('usage: client.py submission_file [host, port]')
        sys.exit(1)

    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, int(port)))
        send_file(sock, filename)
        diff = receive_diff(sock)

        # Print out the diff if the user submitted an incorrect answer
        if diff:
            print("Incorrect repsonse. Here's the diff:\n")
            print(diff, end='')
        else:
            print('You got it right!')
