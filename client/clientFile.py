import math
class clientFile:

    def __init__(self, hasFile, fileSize, pieceSize, copyThis):
        """
        Set up the file class.
        :param hasFile: if the client has the file at set up the value is 1. Otherwise, 0.
        :param fileSize: Size of file.
        :param pieceSize: Size of individual pieces.
        :param copyThis: For neighbors to keep track of their bitField.
        """
        numOfPieces = fileSize // pieceSize
        lastSize = pieceSize
        if fileSize % pieceSize != 0:
            lastSize = fileSize % pieceSize
            numOfPieces += 1
        if copyThis == []:
            for i in range(numOfPieces):
                if i == numOfPieces-1:
                    self.file.append([hasFile for j in range(lastSize)])
                else:
                    self.file.append([hasFile for j in range(pieceSize)])
        else:
            for i in range(numOfPieces):
                val = 0
                if i in copyThis:
                    val = 1
                if i == numOfPieces-1:
                    self.file.append([val for j in range(lastSize)])
                else:
                    self.file.append([val for j in range(pieceSize)])

    def havePieces(self):
        """
        Get a list of the indexes the pieces we have.
        :return: the list of pieces
        """
        ans = []
        for i in range(len(self.file)):
            if self.file[i][0] == 1:
                ans.append(i)
        return ans

    def piecesNeed(self):
        """
        Get a list of the indexes of the pieces we need.
        :return: the list of pieces.
        """
        ans = []
        for i in range(len(self.file)):
            if self.file[i][0] == 0:
                ans.append(i)
        return ans



