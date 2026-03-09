import socket
from memory.PeerState import PeerState


def connect_to_previous_peers(state: PeerState):
    previous = []
    for peer in state.peers:
        if peer["peer_id"] == state.my_peer_id:
            break
        previous.append(peer)

    # connect to all previous peers, perform handshake, vv.
    for peer in previous:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer["host"], peer["port"]))
