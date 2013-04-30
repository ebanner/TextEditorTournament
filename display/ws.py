#!/usr/bin/python3

import socket
import sys
import time

import hashlib
import base64
from hashlib import sha1
from base64 import b64encode

import threading

import atexit

HOST, PORT = 'localhost', 9999
SUBMISSION_SERVER_PORT = 6900
MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

connected = False


def on_exit():
    """Just change terminal colors back to normal."""
    print("\033[0m", end = "")


def get_hash(key):
    """
    Returns the correct hash value from the given key, ready to go, in the
    form of a string. The given key should also be a string.
    """
    accept = bytes(key, 'utf-8') + MAGIC
    accept = sha1(accept).digest()
    accept = base64.encodebytes(accept)
    return accept.decode('utf-8').strip()


def read_data(client):
    """
    Reads the client socket, getting data (in the form of raw bytes), by
    following the protocol. This handles the arbitrary sizing of WebSocket
    protocol headers, and reading the data using a masking key.
    Protocol (to my understanding):
    FRAME -> first 2 bytes
        byte 0: OPCODE: If the 7th bit is set, supposedly this is the last piece
                of the payload. Not sure what this does at this point (ignored).
        byte 1: Indicates how long the length header is. If byte 1 == 126, the
                length is 2 bytes long. If byte 1 == 127, the length is 8 bytes
                long.
    LENGTH -> next 2 or 8 bytes (using byte 1 to differentiate)
        Translate the int of how long the data is (big endian bit order).
    MASK KEY -> next 4 bytes
        Use to decode the raw data sent by the client.
    DATA -> next n bytes (depending on LENGTH)
        Each byte should be XOR'd (bitwise exclusive or) with the MASK KEY byte,
        rotated mod 4 (i.e. first data byte is XOR'd with first MASK KEY,
        second w/ second, third w/ third, fourth w/ fourth, fifth w/ first again,
        and so on. This XOR'd data should be saved as the actual, readable,
        decoded data (as an array of bytes).
    """
    # get first 2 bytes (guaranteed to be header)
    frame = client.recv(2)
    
    # check if the 7th bit in the first byte is set:
    mask = 1 << 7
    first_set = (frame[0] & mask) == 0
    # ignored for now
    
    # second byte should ALWAYS have its 7th bit set
    # (frame[1] & mask) == 0 (should be true)
    
    # get data length from second byte
    data_len = frame[1] & 0x7F
    
    # data_len should be 126 or 127
    if data_len == 126:
        len_bytes = client.recv(2)
        # TODO - only works in python 3.2+
        data_len = int.from_bytes(len_bytes, byteorder='big')
    
    elif data_len == 127:
        len_bytes = client.recv(8)
        # TODO - only works in python 3.2+
        data_len = int.from_bytes(len_bytes, byteorder='big')

    #print('Got message: {} bytes long.'.format(data_len))
    
    # A masking key, used to read
    # Something to do with encryption I think - because it's not like anyone
    #   can just read the protocol, right?
    mask_key = client.recv(4)
    
    # receive the data using the determined data length
    received_bytes = client.recv(data_len)
    
    # construct the data byte array using the received bytes
    data = bytearray(data_len)
    for i, byte in enumerate(received_bytes):
        data[i] = byte ^ mask_key[i%4]
    
    return data


def send_data(client, message):
    """Send a message to the WebSocket client."""
    data = bytearray()
    length = len(message)
    data.append(129) # data[0]
    if length <= 125:
        data.append(length) # data[1]
        
    else: # for now, can't handle more data
        return
    
    # append each character in message
    for c in message:
        data.append(ord(c))
     
    print('WRITE (web browser): {}'.format(data))
    client.sendall(data)


class Receiver(threading.Thread):
    """
    Receiver just reads data and prints it to the screen (so it doesn't block
    the user)
    """
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.client = client;
    
    def run(self):
        global connected
        while True:
            try:
                message = read_data(self.client)
                print("\r\033[93mClient: " + message.decode('utf-8') + "\033[94m")
            except Exception:
                print("\033[0mClient Disconnected. Type anything to quit.")
                connected = False
                break

def read_line(sock_stream):
    """Returns a line read from the submission server socket."""
    line = sock_stream.readline().strip()
    print('READ: {}'.format(line))
    return line

def write_line(sock_stream, message):
    """Writes a message (line) to the submission server socket
    
    In practice, the only line we will be sending will read
             TEXT_EDITOR_TOURNAMENT_TYPE_DISPLAY
    
    """
    print('WRITE (submission server): {}'.format(message))
    sock.sendall(bytes(message + "\n", 'utf-8'))



if __name__ == '__main__':
    # register exit action (function)
    atexit.register(on_exit)
    
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((HOST, int(PORT)))
    listener.listen(0)
    print("Waiting for a client to connect...")
    
    client, addr = listener.accept()
    stream = client.makefile()
    
    # parse incoming data
    message = stream.readline().strip()
    while message:
        msg_list = message.split()
        if msg_list[0] == 'Sec-WebSocket-Key:':
            key = msg_list[1]
        elif msg_list[0] == '':
            pass
        #print(msg_list)
        message = stream.readline().strip()
    
    
    accept = get_hash(key)
    handshake = "HTTP/1.1 101 Switching Protocols\r\n"
    handshake += "Upgrade: websocket\r\n"
    handshake += "Connection: Upgrade\r\n"
    handshake += "Sec-WebSocket-Accept: " + accept + "\r\n"
    #handshake += "Sec-WebSocket-Protocol: chat, superchat\n"
    handshake += "\r\n"
    print(handshake)
    client.sendall(handshake.encode())
    
    connected = True
    #receiver = Receiver(client)
    #receiver.start()
    
    # run a demo test scenario protocol
    x = """
    send_data(client, "CONNECTION_ACCEPTED")
    
    send_data(client, "ADD_PARTICIPANT")
    send_data(client, "Richard")
    send_data(client, "GEdit")
    
    send_data(client, "ADD_PARTICIPANT")
    send_data(client, "Edward")
    send_data(client, "vim")
    
    send_data(client, "ADD_PARTICIPANT")
    send_data(client, "Some Guy")
    send_data(client, "vim")
    
    send_data(client, "ADD_PARTICIPANT")
    send_data(client, "Troll")
    send_data(client, "nano")
    
    send_data(client, "ADD_PARTICIPANT")
    send_data(client, "Nick")
    send_data(client, "Eclipse")
    
    send_data(client, "ADD_PARTICIPANT")
    send_data(client, "Dr. Someguy")
    send_data(client, "emacs")
    
    send_data(client, "ADD_PARTICIPANT")
    send_data(client, "Jimmy")
    send_data(client, "GEdit")
    
    send_data(client, "REMOVE_PARTICIPANT")
    send_data(client, "Jimmy")
    
    time.sleep(8)
    
    send_data(client, "CHALLENGE_INITIATE")
    send_data(client, "1")
    send_data(client, "First Test Challenge")
    send_data(client, "4")
    send_data(client, "This is just a test description, so please ignore it.")
    send_data(client, "Even if you choose to do this challenge, it will not")
    send_data(client, "matter, because we're not actually doing it. Seriously.")
    send_data(client, "Just ignore this. It's for testing purposes only!")
    
    time.sleep(1.5)
    send_data(client, "PARTICIPANT_ACCEPTED")
    send_data(client, "Troll")
    
    time.sleep(1.5)
    send_data(client, "PARTICIPANT_ACCEPTED")
    send_data(client, "Dr. Someguy")
    
    time.sleep(2)
    send_data(client, "PARTICIPANT_ACCEPTED")
    send_data(client, "Richard")
    
    time.sleep(0.1)
    send_data(client, "PARTICIPANT_ACCEPTED")
    send_data(client, "Edward")
    
    time.sleep(4)
    send_data(client, "PARTICIPANT_ACCEPTED")
    send_data(client, "Nick")
    
    time.sleep(5)
    
    send_data(client, "CHALLENGE_START")
    
    time.sleep(0.5)
    send_data(client, "SET_PARTICIPANT_STATUS")
    send_data(client, "Troll")
    send_data(client, "STATUS_FINISHED")
    
    time.sleep(5)
    send_data(client, "INCORRECT_SUBMISSION")
    send_data(client, "Dr. Someguy")
    
    time.sleep(7)
    send_data(client, "SET_PARTICIPANT_STATUS")
    send_data(client, "Edward")
    send_data(client, "STATUS_FINISHED")
    
    time.sleep(4)
    send_data(client, "SET_PARTICIPANT_STATUS")
    send_data(client, "Richard")
    send_data(client, "STATUS_FINISHED")
    
    time.sleep(2)
    send_data(client, "INCORRECT_SUBMISSION")
    send_data(client, "Dr. Someguy")
    
    time.sleep(1.5)
    send_data(client, "SET_PARTICIPANT_STATUS")
    send_data(client, "Nick")
    send_data(client, "STATUS_FINISHED")
    
    time.sleep(5)
    send_data(client, "SET_PARTICIPANT_STATUS")
    send_data(client, "Dr. Someguy")
    send_data(client, "STATUS_FORFEIT")
    
    time.sleep(5)
    send_data(client, "CHALLENGE_FINISH")
    """
    
    # Create the socket to the submission server and try to connect
    #x = """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, int(SUBMISSION_SERVER_PORT)))
    except Exception as e:
        print(e)
        print('Something went wrong with connecting to the server. I quit.')
        exit()

    # Send initial message to Submission Server registering this as a display
    # server.
    server_stream = sock.makefile()
    write_line(server_stream, 'TEXT_EDITOR_TOURNAMENT_TYPE_DISPLAY')
    message = '==*^*=='

    while message:
        # Read updates from the competition and write them to the web browser
        # client.
        message = read_line(server_stream)
        send_data(client, message)
	#"""
    #sock.close()
    client.close()
