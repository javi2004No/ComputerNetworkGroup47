# turn raw byte from socker into structured message, and call correct handler function to handle the message
from utils.helper import recv_msg, recv_exact
from utils.constant import (
    CHOKE_TYPE,
    UNCHOKE_TYPE,
    INTERESTED_TYPE,
    NOT_INTERESTED_TYPE,
    HAVE_TYPE,
    BITFIELD_TYPE,
    REQUEST_TYPE,
    PIECE_TYPE,
)


def parse_msg(msg_type: int, payload: bytes) -> dict:
    if msg_type == CHOKE_TYPE:
        if len(payload) != 0:
            raise ValueError("Choke message should have no payload")
        return {"type": CHOKE_TYPE}
    elif msg_type == UNCHOKE_TYPE:
        if len(payload) != 0:
            raise ValueError("Unchoke message should have no payload")
        return {"type": UNCHOKE_TYPE}
    elif msg_type == INTERESTED_TYPE:
        if len(payload) != 0:
            raise ValueError("Interested message should have no payload")
        return {"type": INTERESTED_TYPE}
    elif msg_type == NOT_INTERESTED_TYPE:
        if len(payload) != 0:
            raise ValueError("Not interested message should have no payload")
        return {"type": NOT_INTERESTED_TYPE}
    elif msg_type == HAVE_TYPE:
        if len(payload) != 4:  # payload need to be exactly 4 bytes
            raise ValueError("Have message should have 4 bytes payload for piece index")
        piece_index = int.from_bytes(payload, byteorder="big")
        return {"type": HAVE_TYPE, "piece_index": piece_index}
    elif msg_type == BITFIELD_TYPE:
        return {"type": BITFIELD_TYPE, "bitfield": payload}
    elif msg_type == REQUEST_TYPE:
        if len(payload) != 4:  # payload need to be exactly 4 bytes
            raise ValueError(
                "Request message should have 4 bytes payload for piece index"
            )
        piece_index = int.from_bytes(payload, byteorder="big")
        return {"type": REQUEST_TYPE, "piece_index": piece_index}
    elif msg_type == PIECE_TYPE:
        if len(payload) < 4:
            raise ValueError(
                "Piece message should have at least 4 bytes payload for piece index"
            )  # since it is the 4 byte piece index + content
        piece_index = int.from_bytes(payload[:4], byteorder="big")
        data = payload[4:]
        return {"type": PIECE_TYPE, "piece_index": piece_index, "data": data}
