class PeerState:
    def __init__(self, my_peer_id: int, common_cfg: dict, peers: list):
        self.my_peer_id = my_peer_id
        self.common_cfg = common_cfg
        self.peers = peers
