import random
import socket
import sys

CACHED_PACKET = ''
MAGIC = '{:x}'.format(random.getrandbits(128))


def last_packet(new_packet):
    """Returns true if the character sequence to end communication has been
    sent.

    When the server is finished sending data, it will send a magic sequence of
    characters to indicate the exchange is finished. Normally, this special
    sequence of characters would be at the end of a packet sent by the server.
    But we have to account for the case that the magic sequence of characters
    gets split on a 1024 byte boundary. So instead of examining the end of a
    packet, we join the last two packets received and check to see if the
    special character sequence is in there.

    """
    global CACHED_PACKET
    packet = ''.join([CACHED_PACKET, new_packet])
    CACHED_PACKET = new_packet

    if MAGIC in packet:
        return True
    else:
        return False

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
        print('Sending {}'.format(data))

    # Send the magic char sequence indicating we are done sending the file
    socket.sendall(bytes(MAGIC + "\n", 'utf-8'))

def receive_diff(socket):
    """Get the diff back from the server"""
    diff = ''

    while True:
        received = str(socket.recv(1024), 'utf-8')

        if last_packet(received):
            break
        else:
            diff = ''.join([diff, received])

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
