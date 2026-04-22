import threading

from memory.MemoryMain import MemoryMain
from server.config import load_common_cfg, load_peer_cfg, get_my_peer_info
from server.server import start_server
from protocol.unchoking_scheduler import start_unchoking_scheduler
import sys
import time
from memory.PeerState import PeerState
from client.client import connect_to_previous_peers


def main():
    # I gonna update the path as well as the peer id later
    common_cfg = load_common_cfg("test-local/Common.cfg")
    peers = load_peer_cfg("test-local/PeerInfo.cfg")
    my_peer_id = int(sys.argv[1])

    my_peer_info = get_my_peer_info(peers, my_peer_id)
    peer_state = PeerState(my_peer_id, common_cfg, peers)
    memory = MemoryMain(peer_state)
    connections = {}
    connections_lock = threading.Lock()

    server_thread = threading.Thread(
        target=start_server,
        args=(
            my_peer_info["host"],
            my_peer_info["port"],
            my_peer_id,
            peer_state,
            memory,
            connections,
            connections_lock,
        ),
        daemon=True,
    )
    server_thread.start()
    time.sleep(1)
    print(f"Prepare to connect to previous peers")
    connect_to_previous_peers(peer_state, memory, connections, connections_lock)

    # Start the unchoking scheduler
    print(f"Starting unchoking scheduler")
    start_unchoking_scheduler(peer_state, memory, connections, connections_lock)

    try:
        while True:
            if memory.is_network_complete():
                print(f"[Network] All peers have complete files. Terminating...")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")


if __name__ == "__main__":
    main()
