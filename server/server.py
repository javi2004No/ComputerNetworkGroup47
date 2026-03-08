import socket
import threading


def handle_client(connection, address):
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            connection.sendall(data)
    finally:
        connection.close()


def start_server(host="127.0.0.1", port=5000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    while True:
        connectionm, address = server_socket.accept()
        threading.Thread(
            target=handle_client, args=(connectionm, address)
        ).start()  # each client will be handled in a separate thread


if __name__ == "__main__":
    start_server()
