from helper import recv_exact
import socket

HEADER = b"P2PFILESHARINGPROJ"
ZEROS = b"\x00" * 10
HANDSHAKE_MSG_LENGTH = 32  # 32 bytes in total


def create_handshake_msg(peer_id: int) -> bytes:
    return (
        HEADER + ZEROS + peer_id.to_bytes(4, byteorder="big")
    )  # struct.pack(">I", peer_id)


def send_handshake(socket, peer_id: int) -> None:
    packet = create_handshake_msg(peer_id)
    socket.sendall(packet)


def recv_handshake(socket, expected_peer_id: int) -> int:
    """
    Receives a handshake message from the socket and validates it.

    We have to validate structure of the message: Check header, check zeros, check peer ID if expected_peer_id is provided.
    """
    data = recv_exact(socket, HANDSHAKE_MSG_LENGTH)
    if not data.startswith(HEADER) or data[18:28] != ZEROS:
        raise ValueError("Invalid handshake message received")
    peer_id = int.from_bytes(data[28:32], byteorder="big")
    if expected_peer_id is not None and peer_id != expected_peer_id:
        raise ValueError(
            f"Handshake failed: expected peer ID {expected_peer_id}, but got {peer_id}"
        )
    return peer_id


def perform_handshake(
    socket: socket.socket, my_peer_id: int, expected_peer_id: int
) -> int:
    """
    Performs handshake, send handshake message and wait for handshake response

    Return peer ID if the hadnshake is successful
    """

    send_handshake(socket, my_peer_id)
    return recv_handshake(socket, expected_peer_id)
