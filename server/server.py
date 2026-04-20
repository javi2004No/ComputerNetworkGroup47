import socket
import threading

from protocol.handshake import perform_incoming_handshake
from server.config import load_common_cfg, load_peer_cfg, get_my_peer_info
from protocol.handle_peer_connection import handle_peer_connection


def handle_incoming_connection(
    connection,
    address,
    my_peer_id,
    peer_state,
    memory,
    connections,
    connections_lock,
):
    try:
        remote_id = perform_incoming_handshake(
            connection,
            my_peer_id,
        )

        with connections_lock:
            connections[remote_id] = connection

        handle_peer_connection(
            socket=connection,
            remote_peer_id=remote_id,
            peer_state=peer_state,
            memory=memory,
            connections=connections,
            connections_lock=connections_lock,
        )

    except Exception as e:
        print(f"Error handling incoming peer {address}: {e}")
    finally:
        try:
            connection.close()
        except:
            pass


# accept -> handshake -> store connection -> send bitfield -> protocol loop
def start_server(
    host="127.0.0.1",
    port=5000,
    my_peer_id=0,
    peer_state=None,
    memory=None,
    connections=None,
    connections_lock=None,
):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"DEBUG host={repr(host)}, port={repr(port)}")
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    while True:
        connection, address = server_socket.accept()
        threading.Thread(
            target=handle_incoming_connection,
            args=(
                connection,
                address,
                my_peer_id,
                peer_state,
                memory,
                connections,
                connections_lock,
            ),
            daemon=True,
        ).start()  # each client will be handled in a separate thread
