from utils.helper import recv_exact
import socket
from utils.constant import HEADER, ZEROS, HANDSHAKE_MSG_LENGTH
from protocol.messages import create_handshake_msg


def send_handshake(socket: socket.socket, peer_id: int) -> None:
    packet = create_handshake_msg(peer_id)
    print(f"Sending handshake {packet} with my peer {peer_id}")
    socket.sendall(packet)
    print(f"Finished sending handshake as peer {peer_id}")


def recv_handshake(socket: socket.socket, expected_peer_id: int) -> int:
    """
    Receives a handshake message from the socket and validates it.

    We have to validate structure of the message: Check header, check zeros, check peer ID if expected_peer_id is provided.
    """
    data = recv_exact(socket, HANDSHAKE_MSG_LENGTH)
    print(f"Received handshake {data} from peer {expected_peer_id}")
    if not data.startswith(HEADER) or data[18:28] != ZEROS:
        raise ValueError("Invalid handshake message received")
    peer_id = int.from_bytes(data[28:32], byteorder="big")
    if expected_peer_id is not None and peer_id != expected_peer_id:
        raise ValueError(
            f"Handshake failed: expected peer ID {expected_peer_id}, but got {peer_id}"
        )
    return peer_id



def perform_outgoing_handshake(
    socket: socket.socket, my_peer_id: int, expected_peer_id: int
) -> int:
    """
    Performs handshake for OUTGOING connections.
    For outgoing connections: send first, then receive.
    
    Return peer ID if the handshake is successful
    """
    send_handshake(socket, my_peer_id)
    return recv_handshake(socket, expected_peer_id)


def perform_incoming_handshake(
    socket: socket.socket, my_peer_id: int
) -> int:
    """
    Performs handshake for INCOMING connections.
    For incoming connections: receive first, then send.
    
    Return peer ID if the handshake is successful
    """
    remote_peer_id = recv_handshake(socket, expected_peer_id=None)
    send_handshake(socket, my_peer_id)
    return remote_peer_id
