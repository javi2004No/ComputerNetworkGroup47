import socket

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
    socket: socket.socket,
    remote_peer_id,
    peer_state,
    memory,
    connections,
    connections_lock,
):
    try:
        print(f"[Peer Connection] Starting protocol loop with peer {remote_peer_id}")
        my_bitfield = memory.get_my_bitfield()
        print(f"[Peer Connection] My bitfield: {my_bitfield}")
        if any(my_bitfield):
            print(f"[Peer Connection] Sending bitfield to peer {remote_peer_id}")
            socket.sendall(create_bitfield_msg(bitfield_to_bytes(my_bitfield)))

        print(f"[Peer Connection] Entering message loop with peer {remote_peer_id}")
        while True:
            msg = read_message(socket)
            print(
                f"[Peer Connection] Received message type {msg['type']} from peer {remote_peer_id}"
            )

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
    except ConnectionError as e:
        print(f"[Peer Connection] Connection error with peer {remote_peer_id}: {e}")
    except Exception as e:
        print(
            f"[Peer Connection] Error in handle_peer_connection with peer {remote_peer_id}: {e}"
        )
        import traceback

        traceback.print_exc()
    finally:
        print(f"[Peer Connection] Closing connection with peer {remote_peer_id}")
        with connections_lock:
            if remote_peer_id in connections:
                del connections[remote_peer_id]
        try:
            socket.close()
        except:
            pass
