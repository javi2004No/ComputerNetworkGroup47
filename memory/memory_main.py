import mem_File
import random
class _data:
    def __init__(self):
        self.bitmap;
        self.choked = True

class memory_main:

    def __init__(self, hasFile, fileSize, chunkSize, interval, num_of_preferred_neighbors):
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

    def add_neighbor(self, name, chunks):
        """
        Creates a bitmap for the neighbor specified by name.
        :param name: The ID of the neighbor.
        :param chunks: The chunks that the neighbor contains.
        """
        self._neighbors[name] = _data()
        self._neighbors[name].bitmap = mem_File(0, self._fileSize, self._chunkSize, chunks)

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
        return list(set(self._bitMap.piecesNeed()) & set(self._neighbors[neighbor].bitmap.havePieces()))

    def all_interests(self):
        """
        Get interests for all the neighbors.
        :return: A list of interests from all neighbors.
        """
        return [interest(neighbor) for neighbor in self._neighbors.keys()]

    def calculate_download_rate(self, downloads):
        """
        Calculates the download rates of all neighbors.
        :param downloads: The amount of data that was downloaded from the neighbors.
        :return: A list of the download rates.
        """
        return [download/self._interval for download in downloads]

    def pick_random_n(self, num, values):
        """
        Picks
        :param num:
        :param values:
        :return:
        """
        ans = []
        for i in range(num):
            ans.append(values.pop(random.randint(0, len(values)-1)))
        return ans



