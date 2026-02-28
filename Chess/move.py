class Move:
    def __init__(self, startSq, endSq, board, enPassant=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.promotionPending = False
        self.enPassant = enPassant

        if enPassant:
            self.pieceCaptured = board[self.startRow][self.endCol]

        
        # compare 1 integer instead of 4, faster
        self.moveID = (
            self.startRow * 1000 +
            self.startCol * 100 +
            self.endRow * 10 +
            self.endCol
        )

    def __eq__(self, other):
        return isinstance(other, Move) and self.moveID == other.moveID

    def __str__(self):
        return f"{self.pieceMoved}: ({self.startRow},{self.startCol}) -> ({self.endRow},{self.endCol})"
    

'''
moveID xample
(startRow)(startCol)(endRow)(endCol)
(6,4) -> (4,4)
6*1000 = 6000
4*100  = 400
4*10   = 40
4      = 4
         6444
'''