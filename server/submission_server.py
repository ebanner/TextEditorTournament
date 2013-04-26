#!/usr/bin/python3

# server
import socket
import sys

# application imports
import boss


# global variables
HOST, PORT = "localhost", 6900
boss = boss.Boss()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ignored_filename, PORT = sys.argv

    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    print('Server started!')

    listener.bind((HOST, int(PORT)))
    listener.listen(5)
    
    print('Waiting for clients...')
    
    while True:
        client, client_addr = listener.accept()
        connection_type = client.makefile().readline().strip()
        print(connection_type)
        if connection_type == "TEXT_EDITOR_TOURNAMENT_TYPE_PARTICIPANT":
            boss.add_participant(client)
        elif connection_type == "TEXT_EDITOR_TOURNAMENT_TYPE_MANAGER":
            boss.set_manager(client)
        elif connection_type == "TEXT_EDITOR_TOURNAMENT_TYPE_DISPLAY":
            boss.set_display(client)
        else:
            # send a reject message and close
            client.sendall(bytes("CONNECTION_REJECTED\n", 'utf-8'))
            client.close()
