import threading
import time
from protocol.messages import create_choke_msg, create_unchoke_msg


def start_unchoking_scheduler(peer_state, memory, connections, connections_lock):
    """
    Starts the unchoking scheduler thread that:
    1. Every unchoking_interval seconds: selects preferred neighbors based on download rates
    2. Every optimistic_unchoking_interval seconds: selects one optimistically unchoked peer

    :param peer_state: The peer state object
    :param memory: The memory manager
    :param connections: Dictionary of active connections
    :param connections_lock: Lock for thread-safe access to connections
    """

    # This is the actual time-based runner of all the unchoking logic written in MemoryMain class
    def run_scheduler():
        last_preferred_update = time.time()
        last_optimistic_update = time.time()

        while True:
            try:
                current_time = time.time()

                # update preferred neighbors every unchoking_interval seconds
                if (
                    current_time - last_preferred_update
                    >= peer_state.unchoking_interval
                ):
                    last_preferred_update = current_time
                    update_preferred_neighbors(memory, connections, connections_lock)

                # update optimistic neighbor every optimistic_unchoking_interval seconds
                if (
                    current_time - last_optimistic_update
                    >= peer_state.optimistic_unchoking_interval
                ):
                    last_optimistic_update = current_time
                    update_optimistic_neighbor(memory, connections, connections_lock)

                time.sleep(0.1)

            except Exception as e:
                print(f"[Unchoking Scheduler] Error: {e}")
                import traceback

                traceback.print_exc()

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()


def update_preferred_neighbors(memory, connections, connections_lock):
    """
    Selects and unchokes preferred neighbors based on download rates.
    Chokes all other neighbors that are not optimistically unchoked.
    """
    try:
        # Get list of interested neighbors with download info (placeholder - no actual tracking yet)
        # For now, just send unchoke to first k neighbors that are interested
        with connections_lock:
            interested_neighbors = []
            for peer_id, connection in connections.items():
                if (
                    memory._neighbors.get(peer_id)
                    and memory._neighbors[peer_id].interestedIn
                ):
                    interested_neighbors.append(peer_id)

        # only proceed if there are interested neighbors
        if not interested_neighbors:
            print(f"[Unchoking Scheduler] No interested neighbors to unchoke")
            return

        # calculate preferred neighbors (in real implementation, would use download rates. check MemoryMain.py)
        download_data = [[peer_id, 0] for peer_id in interested_neighbors]
        unchoke_list, choke_list = memory.pick_preferred_neighbors(download_data)

        print(f"[Unchoking Scheduler] Preferred neighbors update:")
        print(f"  Unchoke: {unchoke_list}")
        print(f"  Choke: {choke_list}")

        # send unchoke messages to those prefered neighbors
        with connections_lock:
            for peer_id in unchoke_list:
                if peer_id in connections:
                    try:
                        connections[peer_id].sendall(create_unchoke_msg())
                        print(f"[Unchoking Scheduler] Sent unchoke to peer {peer_id}")
                    except Exception as e:
                        print(
                            f"[Unchoking Scheduler] Failed to send unchoke to {peer_id}: {e}"
                        )

        # after updating preferred neighbors, we send choke messages
        with connections_lock:
            for peer_id in choke_list:
                if peer_id in connections:
                    try:
                        connections[peer_id].sendall(create_choke_msg())
                        print(f"[Unchoking Scheduler] Sent choke to peer {peer_id}")
                    except Exception as e:
                        print(
                            f"[Unchoking Scheduler] Failed to send choke to {peer_id}: {e}"
                        )

    except Exception as e:
        print(f"[Unchoking Scheduler] Error in update_preferred_neighbors: {e}")
        import traceback

        traceback.print_exc()


def update_optimistic_neighbor(memory, connections, connections_lock):
    """
    Randomly selects one choked interested peer and sends unchoke.
    Chokes the previous optimistically unchoked peer (if different).
    """
    try:
        # get current optimistic neighbor before updating
        old_optimistic = memory._optimistic_neighbor

        # pick new optimistic neighbor
        new_optimistic, choke_peer = memory.pick_optimistic_neighbor()

        print(f"[Unchoking Scheduler] Optimistic unchoke update:")
        print(f"  Old optimistic peer: {old_optimistic}")
        print(f"  New optimistic peer: {new_optimistic}")
        print(f"  Peer to choke: {choke_peer}")

        # if no optimistic neighbor available, nothing to do
        if new_optimistic == -1:
            print(
                f"[Unchoking Scheduler] No interested choked peers available for optimistic unchoking"
            )
            return

        # send unchoke to new optimistic neighbor
        with connections_lock:
            if new_optimistic in connections:
                try:
                    connections[new_optimistic].sendall(create_unchoke_msg())
                    print(
                        f"[Unchoking Scheduler] Sent optimistic unchoke to peer {new_optimistic}"
                    )
                except Exception as e:
                    print(
                        f"[Unchoking Scheduler] Failed to send optimistic unchoke to {new_optimistic}: {e}"
                    )
            else:
                print(
                    f"[Unchoking Scheduler] Optimistic peer {new_optimistic} not in connections"
                )

        # send choke to old optimistic neighbor
        if choke_peer != -1 and choke_peer != new_optimistic:
            with connections_lock:
                if choke_peer in connections:
                    try:
                        connections[choke_peer].sendall(create_choke_msg())
                        print(
                            f"[Unchoking Scheduler] Sent choke to old optimistic peer {choke_peer}"
                        )
                    except Exception as e:
                        print(
                            f"[Unchoking Scheduler] Failed to send choke to {choke_peer}: {e}"
                        )

    except Exception as e:
        print(f"[Unchoking Scheduler] Error in update_optimistic_neighbor: {e}")
        import traceback

        traceback.print_exc()
