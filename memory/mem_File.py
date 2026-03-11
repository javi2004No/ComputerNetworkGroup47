class mem_File:
    def __init__(self, hasFile, fileSize, chunkSize, bitField):
        """
        Set up the file class.
        :param hasFile: if the client has the file at set up the value is 1. Otherwise, 0.
        :param fileSize: Size of file.
        :param chunkSize: Size of individual pieces.
        :param bitField: BitField of the file
        """
        self._chunksCount = fileSize // chunkSize
        self._lastSize = chunkSize  # by default the size of the last chunk is just chunk size, unless it is incomplete.
        if fileSize % chunkSize != 0:
            self._lastSize = fileSize % chunkSize
            self._chunksCount += 1  # is mean the remainder are the size of the last one, we add one more to the total count
        self._chunks = (
            {}
        )  # Made chunks a dictionary that connects id to the chunk itself.
        self._chunkSize = chunkSize
        self._chunksLeft = self._chunksCount
        if hasFile == 1:
            self._chunksLeft = 0
        self._bitField = bitField  # For reference bitfiled is a list where each value in the list is 0 if the chunk does not exist or 1 if it does.

    def getBitField(self):
        """
        Gets the bitfield of the file.
        :return: The bitfield of the file.
        """
        return self._bitField

    def loadChunks(self, filePath):
        """
        Load file into chunk by chunkSize from filePath. Check folder project_config_file_[size].
        """
        with open(filePath, "rb") as f:
            for i in range(self._chunksCount):
                if i < self._chunksCount - 1:
                    chunk = f.read(self._chunkSize)
                else:
                    chunk = f.read(self._lastSize)
                if not chunk:
                    break
                self._chunks[i] = chunk

    def getChunksIndex(self, has: int) -> list[int]:
        """
        Get the list of index of chunk that this peer has. Check bit field to get these indexes.

        :has: 1 if we want the indexes of the chunks that this peer has, 0 if we want the indexes of the chunks that this peer does not have.
        :return: A list of indexes of chunks that this peer has (if has = 1) or does not have (if has = 0).
        """
        ans = []
        for i in range(len(self._bitField)):
            if self._bitField[i] == has:
                ans.append(i)
        return ans

    def getChunks(self, indexes: list[int]) -> list[bytes]:
        """
        Gets the chunks specified by the index values.
        :param indexes: The indexes of the chunks.
        :return: A list of the chunks if we have them or an empty list if we don't.
        """
        ans = []
        for i in indexes:
            if self._bitField[i] == 0:
                ans.append(b"")
            else:
                ans.append(self._chunks[i])
        return ans

    def update(self, indexes: list[int], chunksGiven: list[list[int]]) -> None:
        """
        Updates the file with the requested piece. This function assumes that the indexes directly correspond to.
        :param indexes: The index of the changes piece.
        :param chunksGiven: The piece itself.
        :return: Nothing.
        """
        for k, i in enumerate(indexes):
            if self._bitField[i] == 0:
                self._chunksLeft -= 1
                self._chunks[i] = chunksGiven[k]
            self._bitField[i] = 1

    def isComplete(self) -> bool:
        """
        Checks if we have any chunks left to download.
        :return: returns true if there are no chunks left to download.
        """
        return self._chunksLeft == 0

    def getSizeOfChunk(self, index):
        """
        Gets the size of a chunk.
        :param index: The index of the specified chunk.
        """
        if index == self._chunksCount - 1:
            return self._lastSize
        return self._chunkSize

    def getChunk(self, index):
        """
        Gets the chunk specified by the index value.
        :param index: the index of the chunk.
        :return: The chunk if we have it or an empty list if we don't.
        """
        if self._bitField[index] == 0:
            return []
        return self._chunks[index]
