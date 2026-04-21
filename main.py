import threading

from memory.MemoryMain import MemoryMain
from server.config import load_common_cfg, load_peer_cfg, get_my_peer_info
from server.server import start_server
import sys
import time
from memory.PeerState import PeerState
from client.client import connect_to_previous_peers


def main():
    # I gonna update the path as well as the peer id later
    common_cfg = load_common_cfg(
        "project_config_file_small/project_config_file_small/Common.cfg"
    )
    peers = load_peer_cfg(
        "project_config_file_small/project_config_file_small/PeerInfo_Local_Test.cfg"
    )
    my_peer_id = int(sys.argv[1])

    my_peer_info = get_my_peer_info(peers, my_peer_id)
    peer_state = PeerState(my_peer_id, common_cfg, peers)
    memory = MemoryMain(peer_state)
    start_server(
        my_peer_info["host"],
        my_peer_info["port"],
        my_peer_id,
        peer_state,
        memory,
        {},
        threading.Lock(),
    )  # start with connection = None
    #connect_to_previous_peers(peer_state)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")


if __name__ == "__main__":
    main()
