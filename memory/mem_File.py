import math
class mem_File:

    def __init__(self, hasFile, fileSize, chunkSize, copyThis):
        """
        Set up the file class.
        :param hasFile: if the client has the file at set up the value is 1. Otherwise, 0.
        :param fileSize: Size of file.
        :param chunkSize: Size of individual pieces.
        :param copyThis: For neighbors to keep track of their bitField. It's an array of indexes e.g [0, 3, 4] that
            represent the chunks that the neighbor has in order to copy its bitmap.
        """
        numOfPieces = fileSize // chunkSize
        lastSize = chunkSize
        if fileSize % chunkSize != 0:
            lastSize = fileSize % chunkSize
            numOfPieces += 1
        self._chunks = []
        self._chunksLeft = numOfPieces
        if hasFile == 1:
            self._chunksLeft = 0
        if copyThis == []:
            for i in range(numOfPieces):
                if i == numOfPieces-1:
                    self._chunks.append([hasFile for j in range(lastSize)])
                else:
                    self._chunks.append([hasFile for j in range(chunkSize)])
        else:
            for i in range(numOfPieces):
                val = 0
                if i in copyThis:
                    val = 1
                    self._chunksLeft -= 1
                if i == numOfPieces-1:
                    self._chunks.append([val for j in range(lastSize)])
                else:
                    self._chunks.append([val for j in range(chunkSize)])

    def pieces(self, has):
        ans = []
        for i in range(len(self.chunks)):
            if self._chunks[i][0] == has:
                ans.append(i)
        return ans

    def update(self, indexes, chunksGiven):
        """
        Updates the file with the requested piece. This function assumes that the indexes directly correspond to
        :param indexes: The index of the changes piece.
        :param chunksGiven: The piece itself.
        :return: Nothing.
        """
        for k, i in enumerate(indexes):
            if self._chunks[i][0] == 0 and chunksGiven[k][0] == 1:
                self._chunksLeft -= 1
            elif self._chunks[i][0] == 1 and chunksGiven[k][0] == 0:
                self._chunksLeft += 1
                print("I should not be erasing chunks.")
            self._chunks[i] = chunksGiven[k]

    def complete(self):
        """
        Checks if we have any chunks left to download.
        :return: returns true if there are no chunks left to download.
        """
        return self._chunksLeft == 0




