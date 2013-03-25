import socket
import sys

HOST, PORT = "localhost", 9999

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    with open('foo.txt', 'rb') as f:
        data = f.read()
        sock.sendall(data)

    # Signal that we are done sending the file
    sock.sendall(bytes('XXX' + "\n", 'utf-8'))


    while True:
        received = str(sock.recv(1024), "utf-8")
        if received.strip().endswith('XXX'):
            break
        else:
            print(received)

    print('Outside the while loop')
finally:
    sock.close()

print("Sent:     {}".format(data))
print("Received: {}".format(received))
print('All done')
