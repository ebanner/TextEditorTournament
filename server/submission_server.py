# server library
import socket
import sys

# application imports
import boss


# global variables
HOST, PORT = "localhost", 9999
boss = boss.Boss()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ignored_filename, PORT = sys.argv

    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    print('Server started!')

    listener.bind((HOST, PORT))
    listener.listen(5)
    
    print('Waiting for clients...')
    
    while True:
        client, client_addr = listener.accept()
        connection_type = client.makefile().readline().strip()
        print(connection_type)
        if connection_type == "TEXT_EDITOR_TOURNAMENT_TYPE_PARTICIPANT":
            boss.add_client(client)
        else:
            client.close()
