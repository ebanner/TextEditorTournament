import socket
import sys

CACHED_PACKET = ''

def last_packet(new_packet, magic):
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

    if magic in packet:
        return True
    else:
        return False

if __name__ == '__main__':
    HOST, PORT = "localhost", 9999

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        # Send a magic character sequence that signifies the end of
        # communication.
        magic = 'XXX'
        sock.sendall(bytes(magic + "\n", 'utf-8'))

        with open('foo.txt', 'rb') as f:
            data = f.read()
            sock.sendall(data)

        # Signal that we are done sending the file
        sock.sendall(bytes(magic + "\n", 'utf-8'))

        while True:
            received = str(sock.recv(1024), 'utf-8')
            if last_packet(received, magic):
                break
            else:
                print(received, end='')
    finally:
        sock.close()

    print('All done')
