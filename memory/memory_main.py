import mem_File
import random


class _data:
    def __init__(self):
        self.bitmap
        self.choked = True


class memory_main:

    def __init__(
        self, hasFile, fileSize, chunkSize, interval, num_of_preferred_neighbors
    ):
        """
        Set up the memeory object with the current bitmap.
        :param hasFile: Weather the host has the bitmap or not. 1 if the host has the bitmap. 0 if not.
        :param fileSize: The size of the file.
        :param chunkSize: The size of the chunks separating the file.
        :param interval: The interval time.
        :param num_of_preferred_neighbors: The max number of preferred neighbors.
        """
        self._bitmap = mem_File(hasFile, fileSize, chunkSize, [])
        self._neighbors = {}
        self._fileSize = fileSize
        self._chunkSize = chunkSize
        self._interval = interval
        self._windowSize = num_of_preferred_neighbors
        self._optimistic_neighbor = -1

    def add_neighbor(self, name, chunks):
        """
        Creates a bitmap for the neighbor specified by name.
        :param name: The ID of the neighbor.
        :param chunks: The chunks that the neighbor contains.
        """
        self._neighbors[name] = _data()
        self._neighbors[name].bitmap = mem_File(
            0, self._fileSize, self._chunkSize, chunks
        )

    def update_neighbor(self, name, indexes, chunks):
        """
        Updates the bitmap of the neighbor.
        :param name: The ID of the neighbor.
        :param indexes: The indexes of chunks to update.
        :param chunks: The chunks to replace them with.
        """
        self._neighbors[name].bitmap.update(indexes, chunks)

    def update_bitmap(self, index, chunk):
        """
        Updates a chunk in the current bitmap.
        :param index: The index of the chunk to update.
        :param chunk: What to update the chunk to.
        """
        self._bitMap.update([index], [chunk])

    def interest(self, neighbor):
        """
        Returns what chunks our current client would be interested in from its neighbor. e.g. what chunks do they have
        that we don't.
        :param neighbor: The id of the neighbor we are interested in.
        :return: A list of chunks that we can request from the neighbor.
        """
        return list(
            set(self._bitMap.piecesNeed())
            & set(self._neighbors[neighbor].bitmap.havePieces())
        )

    def all_interests(self):
        """
        Get interests for all the neighbors.
        :return: A list of interests from all neighbors.
        """
        return [interest(neighbor) for neighbor in self._neighbors.keys()]

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
        if not self._bitmap.complete():
            download_rates = calculate_download_rate(downloads)
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
        choke = []
        unchoke = []
        for id, data in self._neighbors:
            if data.choked and id not in to_unchoke:
                choke.append(id)
            elif not data.choked and id in to_unchoke:
                unchoke.append(id)
        return unchoke, choke
