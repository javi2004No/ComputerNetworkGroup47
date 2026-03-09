import mem_File
import random
from PeerState import PeerState


class NeighborData:
    def __init__(self):
        self.file = None
        self.choked = True  # initially choke, only unchoke decided by download rate or optimistic unchoking will be unchoked
        self.interested = False  # whether we is interested in this peer or not
        self.interestedIn = False  # whether this peer is interest in us or not


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
        self._windowSize = peerState.number_of_prefered_neighbors
        self._optimistic_neighbor = -1  # undefined yet

    def add_neighbor(self, name, chunks):
        """
        Creates a bitmap for the neighbor specified by name.
        :param name: The ID of the neighbor.
        :param chunks: The chunks that the neighbor contains.
        """
        self._neighbors[name] = NeighborData()
        self._neighbors[name].file = mem_File(
            0, self._fileSize, self._chunkSize, chunks
        )

    def update_bitmap(self, index, chunk):
        """
        Updates a chunk in the current bitmap.
        :param index: The index of the chunk to update.
        :param chunk: What to update the chunk to.
        """
        self._file.update([index], [chunk])

    def interest(self, neighbor):
        """
        Returns what chunks our current client would be interested in from its neighbor. e.g. what chunks do they have
        that we don't.
        :param neighbor: The id of the neighbor we are interested in.
        :return: A list of chunks that we can request from the neighbor.
        """
        return list(
            set(self._file.pieces(0)) & set(self._neighbors[neighbor].file.pieces(1))
        )

    def all_interests(self):
        """
        Get interests for all the neighbors.
        :return: A list of interests from all neighbors.
        """
        return [self.interest(neighbor) for neighbor in self._neighbors.keys()]

    def calculate_download_rate(self, downloads):
        """
        Calculates the download rates of all neighbors.
        :param downloads: The amount of data that was downloaded from the neighbors. Assumes it's a 2d array with the
        second value in the inner array being the size of the download.
        :return: A list of the download rates.
        """
        return [download[1] / self._interval for download in downloads]

    def pick_random_n(self, num, arr):
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

    def pick_preferred_neighbors(self, downloads):
        """
        Picks the new preferred_neighbors.
        :param downloads: the id of the neighbors followed by the amount of downloads of said neighbor.
        :return: a tuple containing where the first element contains a list of neighbors to unchoke and the second
        contains a list of neighbors to choke.
        """
        to_unchoke = []
        # Will use the download rates to pick its preferred neighbors if the bitmap is not complete otherwise it will
        # just pick randomly
        if not self._file.complete():
            download_rates = self.calculate_download_rate(downloads)
            download_rates.sort(reverse=True)
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
            if data.choked and id not in to_unchoke:
                choke.append(id)
                self._neighbors[id].choke = False
            elif not data.choked and id in to_unchoke:
                unchoke.append(id)
                self._neighbors[id].choke = True
        return unchoke, choke

    def pick_optimistic_neighbor(self):
        """
        Picks a random neighbor that is interested in it and is choked.
        :return: returns the neighbor that should be unchoked and if a neighbor needs to be choked.
        """
        choke = -1
        if (
            self._optimistic_neighbor != -1
            and not self._neighbors[self._optimistic_neighbor].choke
        ):
            choke = self._optimistic_neighbor
        arr = []
        for id, val in self._neighbors.items():
            if not val.choked and val.interested:
                arr.append(id)
        arr = self.pick_random_n(1, id)
        if arr == []:
            self._optimistic_neighbor = -1
        else:
            self._optimistic_neighbor = arr[0]
        return self._optimistic_neighbor, choke
