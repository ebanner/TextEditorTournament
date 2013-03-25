import socket
import sys

CACHED_PACKET = ''
MAGIC = 'XXX'

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

def send_file(submission_socket, filename):
    """Submits a file to submission server for grading"""
    # Send the magic character sequence that signifies the end of
    # communication.
    submission_socket.sendall(bytes(MAGIC + "\n", 'utf-8'))

    # Send the entire file to the submission server
    with open('foo.txt', 'rb') as f:
        data = f.read()
        submission_socket.sendall(data)

    # Send the magic char sequence indicating we have sent the entire file and
    # we will send no more.
    submission_socket.sendall(bytes(MAGIC + "\n", 'utf-8'))

def receive_diff(submission_socket):
    """Get the diff back from the submission server"""
    while True:
        received = str(submission_socket.recv(1024), 'utf-8')
        diff = ''

        if last_packet(received):
            break
        else:
            diff = ''.join([diff, received])

        return diff

if __name__ == '__main__':
    host, port = 'localhost', 9999
    filename = 'foo.txt'

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((host, port))
        # Submit the file to the server for grading
        send_file(sock, filename)
        # Get the diff back from the submission server
        diff = receive_diff(sock)
        print(diff)

    finally:
        sock.close()

    print('All done')
