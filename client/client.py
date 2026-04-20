import socket
from memory.PeerState import PeerState
from protocol.handshake import perform_outgoing_handshake


# Client will responsible for: Connect to previous peers, perform handshake, vv.
# No protocol decision logic here
def connect_to_previous_peers(state: PeerState):
    previous = []
    for peer in state.peers:
        if peer["peer_id"] == state.my_peer_id:
            break
        previous.append(peer)
    print(f"Previous peers to connect: {previous}")

    # connect to all previous peers, perform handshake, vv.
    for peer in previous:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((peer["host"], peer["port"]))
            remote_peer_id = perform_outgoing_handshake(
                sock, state.my_peer_id, peer["peer_id"]
            )
            print(f"Successfully connected to peer {remote_peer_id}")
        except Exception as e:
            print(f"Failed to connect to peer {peer['peer_id']}: {e}")
            sock.close()
