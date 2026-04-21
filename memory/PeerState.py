class PeerState:
    def __init__(self, my_peer_id: int, common_cfg: dict, peers: list) -> None:
        self.my_peer_id = my_peer_id
        self.number_of_preferred_neighbors = common_cfg["NumberOfPreferredNeighbors"]
        self.unchoking_interval = common_cfg["UnchokingInterval"]
        self.optimistic_unchoking_interval = common_cfg["OptimisticUnchokingInterval"]
        self.file_name = common_cfg["FileName"]
        self.file_size = common_cfg["FileSize"]
        self.piece_size = common_cfg["PieceSize"]
        self.peers = peers
        self.has_file = 0
        self.host = None
        self.port = None

        for peer in self.peers:
            if peer["peer_id"] == self.my_peer_id:
                self.has_file = peer["has_file"]
                self.host = peer["host"]
                self.port = peer["port"]
                break
