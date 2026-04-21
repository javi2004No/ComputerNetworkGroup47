from utils.constant import (
    HEADER,
    ZEROS,
    CHOKE_TYPE,
    UNCHOKE_TYPE,
    INTERESTED_TYPE,
    NOT_INTERESTED_TYPE,
    HAVE_TYPE,
    BITFIELD_TYPE,
    REQUEST_TYPE,
    PIECE_TYPE,
)


def create_handshake_msg(peer_id: int) -> bytes:
    return (
        HEADER + ZEROS + peer_id.to_bytes(4, byteorder="big")
    )  # struct.pack(">I", peer_id)


# The first four message just a one byte message with no payload
def create_choke_msg() -> bytes:
    message_len = 1
    return message_len.to_bytes(4, byteorder="big") + CHOKE_TYPE.to_bytes(
        1, byteorder="big"
    )


def create_unchoke_msg() -> bytes:
    message_len = 1
    return message_len.to_bytes(4, byteorder="big") + UNCHOKE_TYPE.to_bytes(
        1, byteorder="big"
    )


def create_interested_msg() -> bytes:
    message_len = 1
    return message_len.to_bytes(4, byteorder="big") + INTERESTED_TYPE.to_bytes(
        1, byteorder="big"
    )


def create_not_interested_msg() -> bytes:
    message_len = 1
    return message_len.to_bytes(4, byteorder="big") + NOT_INTERESTED_TYPE.to_bytes(
        1, byteorder="big"
    )


# Have message have Header (length of message) + type (1 byte) + payload (piece index, 4 bytes)
# sending have message to inform neighbor that we have download a piece, so they can update their neighbor bitmap and decide whether they interest in it or not
def create_have_msg(piece_index: int) -> bytes:
    message_len = 5
    return (
        message_len.to_bytes(4, byteorder="big")
        + HAVE_TYPE.to_bytes(1, byteorder="big")
        + piece_index.to_bytes(4, byteorder="big")
    )


# bitfield message have Header (length of message) + type (1 byte) + payload (bitfield, variable length)
# sending bitfield message to inform neighbor about what pieces we have, so they can decide wheher they are interest or not
def create_bitfield_msg(bitfield: list[int]) -> bytes:
    message_len = 1 + len(bitfield)
    return (
        message_len.to_bytes(4, byteorder="big")
        + BITFIELD_TYPE.to_bytes(1, byteorder="big")
        + bytes(bitfield)
    )


# Request message have Header (length of message) + type (1 byte) + payload (piece index, 4 bytes)
# sending request message to inform neighbor that we want to download a piece, so they can decide whether to send the piece to us or not based on whether they choke us or not
def create_request_msg(piece_index: int) -> bytes:
    message_len = 5
    return (
        message_len.to_bytes(4, byteorder="big")
        + REQUEST_TYPE.to_bytes(1, byteorder="big")
        + piece_index.to_bytes(4, byteorder="big")
    )


# Piece message have Header (length of message) + type (1 byte) + payload (piece index, 4 bytes) + data (variable length)
# sending the actual piece data to neighbor after receiving request message from them, so they can update their file and decide whether to send request message to other neighbors or not based on whether they are interested in us or not
def create_piece_msg(piece_index: int, data: bytes) -> bytes:
    message_len = 5 + len(data)
    return (
        message_len.to_bytes(4, byteorder="big")
        + PIECE_TYPE.to_bytes(1, byteorder="big")
        + piece_index.to_bytes(4, byteorder="big")
        + data
    )
