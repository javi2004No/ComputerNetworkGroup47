def load_common_cfg(path: str):
    cfg = {}

    with open(path, "r") as f:
        for line in f:
            line = line.strip().split()
            key, value = line[0], line[1]
            cfg[key] = value

    # here we parsing to ensure data in correct type, for example, number of pieces should be int, not string
    cfg["NumberOfPreferedNeighbors"] = int(cfg["NumberOfPreferedNeighbors"])
    cfg["UnchokingInterval"] = int(cfg["UnchokingInterval"])
    cfg["OptimisticUnchokingInterval"] = int(cfg["OptimisticUnchokingInterval"])
    cfg["FileName"] = str(cfg["FileName"])
    cfg["FileSize"] = int(cfg["FileSize"])
    cfg["PieceSize"] = int(cfg["PieceSize"])

    return cfg


def load_peer_cfg(path: str):
    peers = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip().split()
            peer_id, host, port, has_file = line[0], line[1], line[2], line[3]
            peers.append(
                {
                    "peer_id": int(peer_id),
                    "host": host,
                    "port": int(port),
                    "has_file": has_file == "1",
                }
            )

    return peers


def get_my_peer_info(peers: list, my_peer_id: int):
    for peer in peers:
        if peer["peer_id"] == my_peer_id:
            return peer
    raise ValueError(f"Peer ID {my_peer_id} not found in peer configuration.")
