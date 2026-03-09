import socket
import sys
import threading

from server.handshake import perform_handshake
from server.config import load_common_cfg, load_peer_cfg, get_my_peer_info


def handle_client(connection, address):
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            connection.sendall(data)
    finally:
        connection.close()


def start_server(host="127.0.0.1", port=5000, my_peer_id=0):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    while True:
        connection, address = server_socket.accept()
        remote_id = perform_handshake(connection, my_peer_id, expected_peer_id=None)
        threading.Thread(
            target=handle_client, args=(connection, address)
        ).start()  # each client will be handled in a separate thread
