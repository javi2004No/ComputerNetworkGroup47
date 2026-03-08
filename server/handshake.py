HEADER = b"P2PFILESHARINGPROJ"
ZEROS = b"\x00" * 10


def create_handshake_msg(peer_id: int) -> bytes:
    return HEADER + ZEROS + peer_id.to_bytes(4, byteorder="big")


# use to parse the hadnshake message
def read_handshake_msg(msg):
    pass


def send_handshake(socket, peer_id: int) -> None:
    pass


def recv_handshake(socket, expected_peer_id: int) -> int:
    pass
