# given the parsed message, call correct handler function to handle the message
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
from memory.MemoryMain import MemoryMain


def dispatch_msg(manager: MemoryMain, msg: dict, peer_id: int):
    msg_type = msg["type"]
    if msg_type == CHOKE_TYPE:
        manager.handle_choke(peer_id)
    elif msg_type == UNCHOKE_TYPE:
        manager.handle_unchoke(peer_id)
    elif msg_type == INTERESTED_TYPE:
        manager.handle_interested(peer_id)
    elif msg_type == NOT_INTERESTED_TYPE:
        manager.handle_not_interested(peer_id)
    elif msg_type == HAVE_TYPE:
        manager.handle_have(peer_id, msg["piece_index"])
    elif msg_type == BITFIELD_TYPE:
        manager.handle_bitfield(peer_id, msg["bitfield"])
    elif msg_type == REQUEST_TYPE:
        manager.handle_request(peer_id, msg["piece_index"])
    elif msg_type == PIECE_TYPE:
        manager.handle_piece(peer_id, msg["piece_index"], msg["data"])
