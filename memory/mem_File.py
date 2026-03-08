import math
class clientFile:

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
        self.chunks = []
        if fileSize % chunkSize != 0:
            lastSize = fileSize % chunkSize
            numOfPieces += 1
        if copyThis == []:
            for i in range(numOfPieces):
                if i == numOfPieces-1:
                    self.chunks.append([hasFile for j in range(lastSize)])
                else:
                    self.chunks.append([hasFile for j in range(chunkSize)])
        else:
            for i in range(numOfPieces):
                val = 0
                if i in copyThis:
                    val = 1
                if i == numOfPieces-1:
                    self.chunks.append([val for j in range(lastSize)])
                else:
                    self.chunks.append([val for j in range(chunkSize)])

    def havePieces(self):
        """
        Get a list of the indexes the pieces we have.
        :return: the list of pieces
        """
        ans = []
        for i in range(len(self.chunks)):
            if self.chunks[i][0] == 1:
                ans.append(i)
        return ans

    def piecesNeed(self):
        """
        Get a list of the indexes of the pieces we need.
        :return: the list of pieces.
        """
        ans = []
        for i in range(len(self.chunks)):
            if self.chunks[i][0] == 0:
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
            self.chunks[i] = indexes[k]




