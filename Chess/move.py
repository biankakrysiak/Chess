class Move:
    rowsToRanks = {7: '1', 6: '2', 5: '3', 4: '4', 3: '5', 2: '6', 1: '7', 0: '8'}
    colsToFiles = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    pieceToNotation = {'K': 'K', 'Q': 'Q', 'R': 'R', 'B': 'B', 'N': 'N', 'P': ''}

    def __init__(self, startSq, endSq, board, enPassant=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.promotionPending = False
        self.promotionPiece = None
        self.enPassant = enPassant
        self.isCastle = False

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
    
    def getNotation(self, isCheck=False, isCheckmate=False, disambig=''):
        file = self.colsToFiles[self.endCol]
        rank = self.rowsToRanks[self.endRow]
        piece = self.pieceMoved[1]
        suffix = '#' if isCheckmate else ('+' if isCheck else '')
        if self.isCastle:
            if self.endCol == 6:
                return 'O-O' + suffix
            else:
                return 'O-O-O' + suffix
            
        capture = ''
        if self.pieceCaptured != '--' or self.enPassant:
            capture = 'x'
            if piece == 'P':
                capture = self.colsToFiles[self.startCol] + 'x'
        pieceStr = '' if piece == 'P' else piece
        promotion = ''
        if self.promotionPending and self.promotionPiece:
            promotion = '=' + self.promotionPiece[1]
        
        return f"{pieceStr}{disambig}{capture}{file}{rank}{promotion}{suffix}"


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