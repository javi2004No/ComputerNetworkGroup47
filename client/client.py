import socket
import threading
from memory.PeerState import PeerState
from protocol.handshake import perform_outgoing_handshake
from protocol.handle_peer_connection import handle_peer_connection
from utils import logger


# Client will responsible for: Connect to previous peers, perform handshake, vv.
# No protocol decision logic here
def connect_to_previous_peers(state: PeerState, memory, connections, connections_lock, log):
    previous = []
    for peer in state.peers:
        if peer["peer_id"] == state.my_peer_id:
            break
        previous.append(peer)
    print(f"Previous peers to connect: {previous}")

    # connect to all previous peers, perform handshake, vv.
    for peer in previous:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)  # 30 second timeout
        try:
            sock.connect((peer["host"], peer["port"]))
            remote_peer_id = perform_outgoing_handshake(
                sock, state.my_peer_id, peer["peer_id"]
            )
            print(f"Successfully connected to peer {remote_peer_id}")
            log.log_tcp_connection(remote_peer_id, True)

            with connections_lock:
                connections[remote_peer_id] = sock

            # Handle the peer connection in a separate thread
            threading.Thread(
                target=handle_peer_connection,
                args=(
                    sock,
                    remote_peer_id,
                    state,
                    memory,
                    connections,
                    connections_lock,
                    log
                ),
                daemon=True,
            ).start()
        except Exception as e:
            print(f"Failed to connect to peer {peer['peer_id']}: {e}")
            sock.close()
