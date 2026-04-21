from memory.mem_File import mem_File
import random
from memory.PeerState import PeerState


class _NeighborData:
    def __init__(self):
        self.file = None
        self.choked = True  # initially choke, only unchoke decided by download rate or optimistic unchoking will be unchoked
        self.interested = False  # whether we are interested in this peer or not
        self.interestedIn = False  # whether this peer is interested in us or not


class MemoryMain:
    def __init__(self, peerState: PeerState) -> None:
        """
        Set up the memory object with the current bitmap.
        :param peerState: The state of the peer containing configuration and peer information.
        """
        bitField = []
        # I am not sure what chunks each thefile have so I assume currently it is either all or nothing, I will update it later when I have more information about the file distribution
        if peerState.has_file == 1:
            bitField = [1] * (peerState.file_size // peerState.piece_size)
        else:
            bitField = [0] * (peerState.file_size // peerState.piece_size)
        self._file = mem_File(
            peerState.has_file, peerState.file_size, peerState.piece_size, bitField
        )
        self._neighbors = {}
        self._fileSize = peerState.file_size
        self._chunkSize = peerState.piece_size
        self._interval = peerState.unchoking_interval
        self._windowSize = peerState.number_of_preferred_neighbors
        self._optimistic_neighbor = -1  # undefined yet
        self._requests = set()  # A set containing all the requests we have sent.
        self._peer_id_to_request = (
            {}
        )  # A dictionary containing what request I have sent to what peer.

    def get_my_bitfield(self):
        return self._file.getBitField()

    def _ensure_neighbor_exists(self, peer_id):
        """
        Ensures a neighbor exists in _neighbors. If not, creates it with an empty bitfield.
        This allows handlers to be called before a bitfield message is received.
        :param peer_id: The ID of the peer.
        """
        if peer_id not in self._neighbors:
            empty_bitfield = [0] * (self._fileSize // self._chunkSize)
            self._neighbors[peer_id] = _NeighborData()
            self._neighbors[peer_id].file = mem_File(
                0, self._fileSize, self._chunkSize, empty_bitfield
            )


    def add_neighbor(self, name, chunks):
        """
        Creates a bitmap for the neighbor specified by name.
        :param name: The ID of the neighbor.
        :param chunks: The chunks that the neighbor contains.
        :return: True if we are interested in the neighbor false otherwise.
        """
        self._neighbors[name] = _NeighborData()
        self._neighbors[name].file = mem_File(
            0, self._fileSize, self._chunkSize, chunks
        )
        if self.interest(name) != []:
            self._neighbors[name].interested = True
            return True
        return False

    def update_neighbor(self, name, indexes, chunks):
        """
        Updates the bitmap of the neighbor. Also updates if we are interested in them now.
        :param name: The ID of the neighbor.
        :param indexes: The indexes of chunks to update.
        :param chunks: The chunks to replace them with.
        :return: return true if we should send an interested message. Warning: False only means we should not send
        any message not that we should send a not interested message.
        """
        self._ensure_neighbor_exists(name)
        self._neighbors[name].file.update(indexes, chunks)
        if not self._neighbors[name].interested and self.interest(name) != []:
            self._neighbors[name].interested = True
            return True
        return False

    def download_bitmap(self, indexes: list[int], downloadChunks) -> None:
        """
        Download a chunk to mem_File. Call mem_File API
        :param index: The index of the chunk to update.
        :param chunk: What to update the chunk to.
        """
        if len(indexes) != len(downloadChunks):
            return
        self._file.update(indexes, downloadChunks)

    def interest(self, neighbor) -> list[int]:
        """
        Returns what chunks our current client would be interested in from its neighbor. e.g. what chunks do they have
        that we don't.
        :param neighbor: The id of the neighbor we are interested in.
        :return: A list of chunks that we can request from the neighbor.
        """
        return list(
            set(self._file.getChunksIndex(0))
            & set(self._neighbors[neighbor].file.getChunksIndex(1))
        )

    def all_interests(self) -> list[list[int]]:
        """
        Get interests for all the neighbors and checks weather we need to send a message.
        :return: A list of interests from all neighbors in the format of [neighbor, piece_index1, piece_index2, ...].
        If we are not interested in a neighbor and we need to send a not-interested message return [neighbor, -1] for
        that neighbor. Else if we already sent the non-interested message return [neighbor, -2].
        """
        fullInterests = []
        for neighbor in self._neighbors.keys():
            interestedIn = self.interest(neighbor)
            if interestedIn == []:
                if self._neighbors[neighbor].interested:
                    fullInterests.append([neighbor, -1])
                    self._neighbors[neighbor].interested = False
                else:
                    fullInterests.append([neighbor, -2])

            else:
                fullInterests.append([neighbor] + interestedIn)
        return fullInterests

    def calculate_download_rate(self, downloads) -> list[float]:
        """
        Calculates the download rates of all neighbors.
        :param downloads: The amount of data that was downloaded from the neighbors. Assumes it's a 2d array with the
        second value in the inner array being the size of the download.
        :return: A list of the download rates.
        """
        return [download[1] / self._interval for download in downloads]

    def pick_random_n(self, num: int, arr: list) -> list[int]:
        """
        Picks a number of values randomly.
        :param num: how many values should be picked.
        :param arr: the values to pick from.
        :return: list of a random selection of values from values.
        """
        if num >= len(arr):
            return arr
        ans = []
        for i in range(num):
            ans.append(arr.pop(random.randint(0, len(arr) - 1)))
        return ans

    def pick_preferred_neighbors(self, downloads) -> tuple[list[int], list[int]]:
        """
        Picks the new preferred_neighbors.
        :param downloads: the id of the neighbors followed by the amount of downloads of said neighbor.
        :return: a tuple containing where the first element contains a list of neighbors to unchoke and the second
        contains a list of neighbors to choke.
        """
        to_unchoke = []
        # Will use the download rates to pick its preferred neighbors if the bitmap is not complete otherwise it will
        # just pick randomly
        if not self._file.isComplete():
            download_rates = self.calculate_download_rate(downloads)
            download_rates.sort(
                reverse=True
            )  # pick based on top fastest download rates
            cur = 0
            while cur < self._windowSize:
                i = cur
                rate = download_rates[i]
                while i < len(download_rates) and rate == download_rates[i]:
                    i += 1
                downloads_selected = []
                if i > self._windowSize:
                    downloads_selected = self.pick_random_n(i - cur, downloads[cur:i])
                else:
                    downloads_selected = downloads[cur:i]
                for download in downloads_selected:
                    to_unchoke.append(download[0])
                cur = i
        else:
            downloads_selected = self.pick_random_n(self._windowSize, downloads)
            for download in downloads_selected:
                to_unchoke.append(download[0])
        # Only returns the changing neighbors e.g neighbors that are choked and need to be unchoked and vice versa.
        # Also assumes that nothing will go wrong in the sending choking/unchoking message part.
        choke = []
        unchoke = []
        for id, data in self._neighbors.items():
            if (
                data.choked and id in to_unchoke
            ):  # Vinh: Edit condition here to only unchoke peers that are in the to_unchoke list and currently choked.
                unchoke.append(id)
                self._neighbors[id].choked = False
            elif not data.choked and id not in to_unchoke:
                choke.append(id)
                self._neighbors[id].choked = True
        return unchoke, choke

    def pick_optimistic_neighbor(self):
        """
        Picks a random neighbor that is interested in it and is choked.
        :return: returns the neighbor that should be unchoked and if a neighbor needs to be choked.
        """
        choked = -1
        if (
            self._optimistic_neighbor != -1
            and self._neighbors[self._optimistic_neighbor].choked
        ):
            choked = self._optimistic_neighbor
        arr = []
        for id, val in self._neighbors.items():
            if (
                val.choked and val.interested
            ):  # Vinh: Edit condition here to only consider peers interested in us and choked.
                arr.append(id)
        arr = self.pick_random_n(1, arr)
        if arr == []:
            self._optimistic_neighbor = -1
        else:
            self._optimistic_neighbor = arr[0]
        return self._optimistic_neighbor, choked

    # --------------------from here will be peer controller script that will be triggered on event of protocol-------------------------------------
    def pick_request(self, peer_id):
        """
        Picks a piece to request from a specific peer following random selection strategy.
        :param peer_id: The ID of the peer we are requesting a piece from.
        :return: Returns the index of the piece we are interested in. If we are not interested in any piece returns -1.
        """
        self._ensure_neighbor_exists(peer_id)
        if not self._neighbors[peer_id].interested:
            return -1
        possible_requests = set(self.interest(peer_id)) - self._requests
        if not possible_requests:
            return -1
        self._peer_id_to_request[peer_id] = self.pick_random_n(1, possible_requests)[0]
        self._requests.add(self._peer_id_to_request[peer_id])
        return self._peer_id_to_request[peer_id]

    def handle_choke(self, peer_id):
        """
        Handles receiving a choke message from a peer.
        :param peer_id: The ID of the sender.
        """
        if peer_id in self._peer_id_to_request.keys():
            self._requests.pop(self._peer_id_to_request[peer_id])
            self._peer_id_to_request.pop(peer_id)

    def handle_unchoke(self, peer_id):
        """
        Handles receiving an unchoke message from a peer.
        :param peer_id: The ID of the sender.
        :return: Returns the index of the piece we want to request from the peer specified in peer_id. returns -1 if
        we are not interested in any piece.
        """
        return self.pick_request(peer_id)

    def handle_interested(self, peer_id):
        """
        Handles receiving an interested message from a peer.
        :param peer_id: The ID of the sender.
        """
        self._ensure_neighbor_exists(peer_id)
        self._neighbors[peer_id].interestedIn = True

    def handle_not_interested(self, peer_id):
        """
        Handles receiving a not interested message from a peer.
        :param peer_id: The ID of the sender.
        """
        self._ensure_neighbor_exists(peer_id)
        self._neighbors[peer_id].interestedIn = False

    def handle_have(self, peer_id, piece_index):
        """
        Handles receiving a have message from a peer.
        :param peer_id: The ID of the sender.
        :param piece_index: The index of the piece.
        :return: True if we should send an interested message false otherwise. False means we should not send any message.
        """
        return self.update_neighbor(peer_id, [piece_index], [[]])

    def handle_bitfield(self, peer_id, bitfield):
        """
        Handles receiving a bitfield message from a peer.
        :param peer_id: The ID of the sender.
        :param bitfield: The bitfield data in the message.
        :return: True if we should send an interested message to the peer. False if we should send a not interested
        message to the peer.
        """
        return self.add_neighbor(peer_id, bitfield)

    def handle_request(self, peer_id, piece_index):
        """
        Handles receiving a request message from a peer.
        :param peer_id: The ID of the sender.
        :param piece_index: The index of the piece requested.
        :return: Returns the chunk if either the neighbor is unchoked because it's a preferred neighbor or if it's the
        optimistic neighbor. Returns an empty list if this is not true or this instance does not have the chunk
        specified.
        """
        self._ensure_neighbor_exists(peer_id)
        if self._neighbors[peer_id].choked and peer_id != self._optimistic_neighbor:
            return []
        return self._file.getChunk(piece_index)

    def handle_piece(self, peer_id, piece_index, data):
        """
        Handles receiving a piece message from a peer.
        :param peer_id: The ID of the sender of the message.
        :param piece_index: The index of the chunk given.
        :param data: The data in need of downloading.
        :return: returns a tuple contain three values in this order: First, we have a list of peer_id's to send a
        not-interested message to. If there is no such peers the list is empty. Second, we have the index of the piece
        we wish to request from the same peer specified by peer_id. If we are not interested in any pieces we return -1.
        Third, we have an int representing the length of the piece we downloaded.
        """
        self._file.update([piece_index], [data])
        fullInterest = self.all_interests()
        not_interested_message = []
        for neighbor in fullInterest:
            if neighbor[1] == -1:
                not_interested_message.append(neighbor[0])
        return (
            not_interested_message,
            self.pick_request(peer_id),
            self._file.getSizeOfChunk(piece_index),
        )
