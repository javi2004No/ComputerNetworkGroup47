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
    INTERESTED_TYPE,
    NOT_INTERESTED_TYPE,
    CHOKE_TYPE,
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
            
            # Handle message responses based on message type
            if msg["type"] == CHOKE_TYPE:
                print(f"[Peer Connection] Peer {remote_peer_id} choked us")
            elif msg["type"] == UNCHOKE_TYPE:
                print(f"[Peer Connection] Peer {remote_peer_id} unchoked us")
                piece_index = result
                if piece_index != -1:
                    print(f"[Peer Connection] Requesting piece {piece_index} from peer {remote_peer_id}")
                    socket.sendall(create_request_msg(piece_index))
            elif msg["type"] == INTERESTED_TYPE:
                print(f"[Peer Connection] Peer {remote_peer_id} is interested")
            elif msg["type"] == NOT_INTERESTED_TYPE:
                print(f"[Peer Connection] Peer {remote_peer_id} is NOT interested")
            elif msg["type"] == HAVE_TYPE:
                print(f"[Peer Connection] Peer {remote_peer_id} has piece {msg.get('piece_index', '?')}")
                if result:
                    print(f"[Peer Connection] Sending interested to peer {remote_peer_id}")
                    socket.sendall(create_interested_msg())
            elif msg["type"] == BITFIELD_TYPE:
                if result:
                    print(f"[Peer Connection] Sending interested to peer {remote_peer_id}")
                    socket.sendall(create_interested_msg())
                else:
                    print(f"[Peer Connection] Sending not interested to peer {remote_peer_id}")
                    socket.sendall(create_not_interested_msg())
            elif msg["type"] == REQUEST_TYPE:
                piece_index = msg.get("piece_index", -1)
                piece_data = result
                if piece_index != -1 and piece_data is not None and piece_data != []:
                    print(f"[Peer Connection] Sending piece {piece_index} to peer {remote_peer_id}")
                    socket.sendall(create_piece_msg(piece_index, bytes(piece_data)))
                else:
                    print(f"[Peer Connection] Cannot send piece {piece_index} to peer {remote_peer_id} (choked or don't have it)")
            elif msg["type"] == PIECE_TYPE:
                piece_index = msg.get("piece_index", -1)
                print(f"[Peer Connection] Received piece {piece_index} from peer {remote_peer_id}")
                not_interested_peers, next_req, piece_size = result
                # Send not interested messages to peers that no longer have interesting pieces
                for peer_id in not_interested_peers:
                    if peer_id != remote_peer_id and peer_id in connections:
                        print(f"[Peer Connection] Sending not interested to peer {peer_id}")
                        try:
                            connections[peer_id].sendall(create_not_interested_msg())
                        except:
                            pass
                # Request next piece from same peer if available
                if next_req != -1:
                    print(f"[Peer Connection] Requesting next piece {next_req} from peer {remote_peer_id}")
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
