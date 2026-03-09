from server.config import load_common_cfg, load_peer_cfg, get_my_peer_info
from server.server import start_server
import sys
from memory.PeerState import PeerState
from client.client import connect_to_previous_peers


def main():
    # I gonna update the path as well as the peer id later
    common_cfg = load_common_cfg("Common.cfg")
    peers = load_peer_cfg("PeerInfo.cfg")
    my_peer_id = int(sys.argv[1])

    my_peer_info = get_my_peer_info(peers, my_peer_id)
    start_server(my_peer_info["host"], my_peer_info["port"], my_peer_id)
    peer_state = PeerState(my_peer_id, common_cfg, peers)
    connect_to_previous_peers(peer_state)


if __name__ == "__main__":
    main()
