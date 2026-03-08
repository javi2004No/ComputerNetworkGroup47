import socket


def start_client(host="127.0.0.1", port=5000):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(b"Hello, Server!")
    response = client_socket.recv(4096)
    print(f"Received from server: {response.decode()}")
    client_socket.close()


if __name__ == "__main__":
    start_client()
