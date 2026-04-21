from protocol.dispatcher import dispatch_msg
from protocol.parser import read_message
from protocol.messages import (
    create_bitfield_msg,
    create_interested_msg,
    create_not_interested_msg,
    create_request_msg,
    create_piece_msg,
    create_have_msg,
)

from protocol.bitfield import bitfield_to_bytes, bytes_to_bitfield
from utils.constant import (
    HAVE_TYPE,
    BITFIELD_TYPE,
    UNCHOKE_TYPE,
    REQUEST_TYPE,
    PIECE_TYPE,
)


def handle_peer_connection(
    socket, remote_peer_id, peer_state, memory, connections, connections_lock
):
    my_bitfield = memory.get_my_bitfield()
    if any(my_bitfield):
        socket.sendall(create_bitfield_msg(bitfield_to_bytes(my_bitfield)))

    while True:
        msg = read_message(socket)

        result = dispatch_msg(manager=memory, msg=msg, peer_id=remote_peer_id)
        if msg["type"] == HAVE_TYPE:
            if result:
                socket.sendall(create_interested_msg())
        elif msg["type"] == BITFIELD_TYPE:
            if result:
                socket.sendall(create_interested_msg())
            else:
                socket.sendall(create_not_interested_msg())
        elif msg["type"] == UNCHOKE_TYPE:
            piece_index = result
            if piece_index != -1:
                socket.sendall(create_request_msg(piece_index))

        elif msg["type"] == REQUEST_TYPE:
            piece_index, data = result
            if piece_index != -1 and data is not None:
                socket.sendall(create_piece_msg(piece_index, bytes(data)))

        elif msg["type"] == PIECE_TYPE:
            not_interestd_peers, next_req, _ = result
            if next_req != -1:
                socket.sendall(create_request_msg(next_req))
