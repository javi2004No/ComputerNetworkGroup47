import socket
import threading
from memory.PeerState import PeerState
from protocol import handshake


# Client will responsible for: Connect to previous peers, perform handshake, vv.
# No protocol decision logic here
def connect_to_previous_peers(state: PeerState, sock):
    previous = []
    for peer in state.peers:
        if peer["peer_id"] == state.my_peer_id:
            break
        previous.append(peer)

    # connect to all previous peers, perform handshake, vv.
    for peer in previous:
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((peer["host"], peer["port"]))
        handshake.send_handshake(sock, state.my_peer_id)

