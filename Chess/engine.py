# Stores informations about current state of the game. 
# Shows valid moves. Keeps move logs.
from move import Move

class ChessEngine:
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
             ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
             ['--', '--','--', '--','--', '--','--', '--'],
             ['--', '--','--', '--','--', '--','--', '--'],
             ['--', '--','--', '--','--', '--','--', '--'],
             ['--', '--','--', '--','--', '--','--', '--'],
             ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
             ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingMoved = False
        self.blackKingMoved = False
        self.whiteKingsRookMoved = False
        self.whiteQueensRookMoved = False
        self.blackKingsRookMoved = False
        self.blackQueensRookMoved = False
        self.enPassantTarget = None
        self.whiteKingPos = (7,4)
        self.blackKingPos = (0,4)
        self.checkingAttack = False
        self.checkmate = False
        self.stalemate = False
        self.positionHistory = {}

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.enPassantTarget = None

        # update king rook moved flags, for castling
        if move.pieceMoved == 'wK':
            self.whiteKingMoved = True
            self.whiteKingPos = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingMoved = True
            self.blackKingPos = (move.endRow, move.endCol)
        elif move.pieceMoved == 'wR':
            if move.startRow == 7 and move.startCol == 0:
                self.whiteQueensRookMoved = True
            elif move.startRow == 7 and move.startCol == 7:
                self.whiteKingsRookMoved = True
        elif move.pieceMoved == 'bR':
            if move.startRow == 0 and move.startCol == 0:
                self.blackQueensRookMoved = True
            elif move.startRow == 0 and move.startCol == 7:
                self.blackKingsRookMoved = True        

        # handle castling
        if move.pieceMoved[1] == 'K' and abs(move.endCol - move.startCol) == 2:
            move.isCastle = True
            if move.endCol == 6:  # kingside
                rookStartCol = 7
                rookEndCol = 5
            else:  # queenside
                rookStartCol = 0
                rookEndCol = 3
            self.board[move.endRow][rookEndCol] = self.board[move.endRow][rookStartCol]
            self.board[move.endRow][rookStartCol] = "--"

            # update rook flags
            if self.whiteToMove:
                if rookStartCol == 7:
                    self.whiteKingsRookMoved = True
                else:
                    self.whiteQueensRookMoved = True
            else:
                if rookStartCol == 7:
                    self.blackKingsRookMoved = True
                else:
                    self.blackQueensRookMoved = True        
        # pawn promotion
        if move.pieceMoved[1] == "P" and (move.endRow == 0 or move.endRow == 7):
            move.promotionPending = True
        # en passant 
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            midRow = (move.startRow + move.endRow) // 2
            self.enPassantTarget = (midRow, move.startCol)
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--"

        self.whiteToMove = not self.whiteToMove
        key = self._boardKey()
        self.positionHistory[key] = self.positionHistory.get(key, 0) + 1

    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != "--":
                    if (self.whiteToMove and piece[0] == "w") or (not self.whiteToMove and piece[0] == "b"):
                        if piece[1] == "P":  # pawns
                            self.getPawnMoves(r, c, moves)
                        elif piece[1] == "R":
                            self.getRookMoves(r, c, moves)
                        elif piece[1] == "B":
                            self.getBishopMoves(r, c, moves)
                        elif piece[1] == "N":
                            self.getKnightMoves(r, c, moves)
                        elif piece[1] == "Q":
                            self.getQueenMoves(r, c, moves)
                        elif piece[1] == "K":
                            self.getKingMoves(r, c, moves)
                        else:
                            return 0
        return moves # list of possible moves for current player
    
    def getPawnMoves(self, r, c, moves): # TBD EN PASSANT and promotion
        if self.whiteToMove: # white pawn
            # 1 square forward
            if r-1 >= 0 and self.board[r-1][c] == "--":
                moves.append(Move((r,c), (r-1, c), self.board))
                # 2 squares forward from starting row
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c), (r-2, c), self.board))
            
            # captures, diagonally left
            if c-1 >= 0 and r-1 >= 0:
                if self.board[r-1][c-1] != "--" and self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            # diagonally right
            if c+1 <= 7 and r-1 >= 0:
                if self.board[r-1][c+1] != "--" and self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
            if (r-1, c-1) == self.enPassantTarget:
                moves.append(Move((r,c),(r-1,c-1), self.board, enPassant=True))
            if (r-1, c+1) == self.enPassantTarget:
                moves.append(Move((r,c),(r-1,c+1), self.board, enPassant=True))

        else: # black pawn
            # 1 square forward
            if r+1 <= 7 and self.board[r+1][c] == "--":
                moves.append(Move((r,c), (r+1,c), self.board))
                # 2 squares forward
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c), (r+2,c), self.board))
            
            # captures, diagonally left
            if c-1 >= 0 and r+1 <= 7:
                if self.board[r+1][c-1] != "--" and self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            # diagonally right
            if c+1 <= 7 and r+1 <= 7:
                if self.board[r+1][c+1] != "--" and self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))
            if (r+1, c-1) == self.enPassantTarget:
                moves.append(Move((r,c),(r+1,c-1), self.board, enPassant=True))
            if (r+1, c+1) == self.enPassantTarget:
                moves.append(Move((r,c),(r+1,c+1), self.board, enPassant=True))

    def pieceMoves(self, directions, r, c, moves, slide=True):
        # generate all possible moves from position (r,c) for current player
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            dr, dc = d
            row, col = r+dr, c+dc
            while 0 <= row <= 7 and 0 <= col <= 7:
                square = self.board[row][col]
                if square == "--":
                    moves.append(Move((r, c), (row, col), self.board))
                elif square[0] == enemyColor:
                    moves.append(Move((r, c), (row, col), self.board))
                    break
                else:
                    break
                if not slide:
                    break
                row = dr + row
                col = dc + col   
    
    def getRookMoves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        self.pieceMoves(directions, r, c, moves)          

    def getBishopMoves(self, r, c, moves):
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]  # up-left, up-right, down-left, down-right
        self.pieceMoves(directions, r, c, moves)
    
    def getQueenMoves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), 
                      (-1,-1), (-1,1), (1,-1), (1,1)]
        self.pieceMoves(directions, r, c, moves)
    
    def getKnightMoves(self, r, c, moves):
        directions = [(-2,-1), (-2,1), (-1,-2), (-1,2),
                        (1,-2),  (1,2),  (2,-1),  (2,1)]
        self.pieceMoves(directions, r, c, moves, slide=False) 
        # knights jump directly to squares, only one possible square per move direction - doesn't need the loop
    
    def getKingMoves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),  # straight
              (-1, -1), (-1, 1), (1, -1), (1, 1)] # diagonal
        self.pieceMoves(directions, r, c, moves, slide=False) 
        if not self.checkingAttack:    
            self.getCastleMoves(r, c, moves)

    def getCastleMoves(self, r, c, moves):
        attackerIsWhite = not self.whiteToMove
        if self.isSquareAttacked(r, c, byWhite=attackerIsWhite):
            return
        
        if self.whiteToMove:
            if not self.whiteKingMoved:
                # Kingside
                if not self.whiteKingsRookMoved and self.board[7][5] == "--" and self.board[7][6] == "--":
                    if not self.isSquareAttacked(7, 5, byWhite=attackerIsWhite) and not self.isSquareAttacked(7, 6, byWhite=attackerIsWhite):
                        moves.append(Move((7, 4), (7, 6), self.board))  # king moves 2 squares
                # Queenside
                if not self.whiteQueensRookMoved and self.board[7][1] == "--" and self.board[7][2] == "--" and self.board[7][3] == "--":
                    if not self.isSquareAttacked(7, 3, byWhite=attackerIsWhite) and not self.isSquareAttacked(7, 2, byWhite=attackerIsWhite):
                        moves.append(Move((7, 4), (7, 2), self.board))
        else:
            if not self.blackKingMoved:
                # Kingside
                if not self.blackKingsRookMoved and self.board[0][5] == "--" and self.board[0][6] == "--":
                    if not self.isSquareAttacked(0, 5, byWhite=attackerIsWhite) and not self.isSquareAttacked(0, 6, byWhite=attackerIsWhite):
                        moves.append(Move((0, 4), (0, 6), self.board))
                # Queenside
                if not self.blackQueensRookMoved and self.board[0][1] == "--" and self.board[0][2] == "--" and self.board[0][3] == "--":
                    if not self.isSquareAttacked(0, 3, byWhite=attackerIsWhite) and not self.isSquareAttacked(0, 2, byWhite=attackerIsWhite):
                        moves.append(Move((0, 4), (0, 2), self.board))

    # checks section
    def getValidMoves(self):
    # save state that undoMove can't restore
        savedFlags = (self.whiteKingMoved, self.blackKingMoved,
                      self.whiteKingsRookMoved, self.whiteQueensRookMoved,
                      self.blackKingsRookMoved, self.blackQueensRookMoved,
                      self.enPassantTarget)
        savedHistory = self.positionHistory.copy()
        moves = self.getAllPossibleMoves()
        validMoves = []
        for move in moves:
            self.makeMove(move)
            if not self.whiteToMove: # white moved
                inCheck = self.isSquareAttacked(self.whiteKingPos[0], self.whiteKingPos[1], byWhite=False)
            else:  # black moved
                inCheck = self.isSquareAttacked(self.blackKingPos[0], self.blackKingPos[1], byWhite=True)
            if not inCheck:
                validMoves.append(move)
            self.undoMove()
            # restore flags after each undo
            (self.whiteKingMoved, self.blackKingMoved,
             self.whiteKingsRookMoved, self.whiteQueensRookMoved,
             self.blackKingsRookMoved, self.blackQueensRookMoved,
             self.enPassantTarget) = savedFlags
            self.positionHistory = savedHistory.copy()
            
        if len(validMoves) == 0:
            if self.whiteToMove:
                inCheck = self.isSquareAttacked(self.whiteKingPos[0], self.whiteKingPos[1], byWhite=False)
            else:
                inCheck = self.isSquareAttacked(self.blackKingPos[0], self.blackKingPos[1], byWhite=True)

            if inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        if self.isThreefoldRepetition():  # <-- dodaj tu
            self.stalemate = True

        return validMoves
    
    def isSquareAttacked(self, r, c, byWhite):
        savedTurn = self.whiteToMove
        self.whiteToMove = byWhite # generate attacker moves
        self.checkingAttack = True
        attackerMoves = self.getAllPossibleMoves()
        self.checkingAttack = False
        self.whiteToMove = savedTurn # undo

        for move in attackerMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def inCheck(self):
        if self.whiteToMove:
            # white moved = black move = does white attack the black king
            return self.isSquareAttacked(self.blackKingPos[0], self.blackKingPos[1], byWhite=True)
        else:
            return self.isSquareAttacked(self.whiteKingPos[0], self.whiteKingPos[1], byWhite=False)

    def undoMove(self):
        if len(self.moveLog) == 0:
            return

        move = self.moveLog.pop()

        self.board[move.startRow][move.startCol] = move.pieceMoved
        self.board[move.endRow][move.endCol] = move.pieceCaptured

        self.whiteToMove = not self.whiteToMove

        if move.pieceMoved == "wK":
            self.whiteKingPos = (move.startRow, move.startCol)
        elif move.pieceMoved == "bK":
            self.blackKingPos = (move.startRow, move.startCol)

        # undo castling
        if move.pieceMoved[1] == 'K' and abs(move.endCol - move.startCol) == 2:
            if move.endCol == 6:  # kingside
                self.board[move.endRow][7] = self.board[move.endRow][5]
                self.board[move.endRow][5] = "--"
            else:  # queenside
                self.board[move.endRow][0] = self.board[move.endRow][3]
                self.board[move.endRow][3] = "--"

        # undo en passant
        if move.enPassant:
            self.board[move.endRow][move.endCol] = "--"
            self.board[move.startRow][move.endCol] = move.pieceCaptured  # restore captured pawn
        
        key = self._boardKey()
        if key in self.positionHistory:
            self.positionHistory[key] -= 1
            if self.positionHistory[key] == 0:
                del self.positionHistory[key]

    # notation 
    def getMoveNotation(self, move):
        # after makeMove, whiteToMove is already flipped
        # so whiteToMove=True means black just moved, whiteToMove=False means white just moved
        isCheckmate = False
        isCheck = False

        if self.whiteToMove:
            # black just moved - check if white king is in check
            isCheck = self.isSquareAttacked(self.whiteKingPos[0], self.whiteKingPos[1], byWhite=False)
        else:
            # white just moved - check if black king is in check
            isCheck = self.isSquareAttacked(self.blackKingPos[0], self.blackKingPos[1], byWhite=True)

        # disambiguation - if two pieces of the same type can move to the same square
        disambig = ''
        if move.pieceMoved[1] not in ('P', 'K'):
            ambiguous = []
            for m in self.getAllPossibleMoves():
                if m != move and m.pieceMoved == move.pieceMoved and \
                   m.endRow == move.endRow and m.endCol == move.endCol:
                    ambiguous.append(m)
            if ambiguous:
                sameCol = any(m.startCol == move.startCol for m in ambiguous)
                sameRow = any(m.startRow == move.startRow for m in ambiguous)
                if not sameCol:
                    disambig = Move.colsToFiles[move.startCol]
                elif not sameRow:
                    disambig = Move.rowsToRanks[move.startRow]
                else:
                    disambig = Move.colsToFiles[move.startCol] + Move.rowsToRanks[move.startRow]

        return move.getNotation(isCheck, isCheckmate, disambig)

    # for arrows in game, showing previous moves
    def getBoardAtMove(self, index): 
        # rebuild board to move index
        board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        for i, move in enumerate(self.moveLog[:index]):
            board[move.startRow][move.startCol] = '--'
            board[move.endRow][move.endCol] = move.pieceMoved
            if move.pieceMoved[1] == 'K' and abs(move.endCol - move.startCol) == 2:
                if move.endCol == 6:
                    board[move.endRow][5] = board[move.endRow][7]
                    board[move.endRow][7] = '--'
                else:
                    board[move.endRow][3] = board[move.endRow][0]
                    board[move.endRow][0] = '--'
            if move.enPassant:
                board[move.startRow][move.endCol] = '--'
            if move.promotionPiece:
                board[move.endRow][move.endCol] = move.promotionPiece
        return board
    
    def _boardKey(self):
        board_str = ''.join(''.join(row) for row in self.board)
        flags = (self.whiteToMove,
                 self.whiteKingMoved, self.blackKingMoved,
                 self.whiteKingsRookMoved, self.whiteQueensRookMoved,
                 self.blackKingsRookMoved, self.blackQueensRookMoved,
                 self.enPassantTarget)
        return board_str + str(flags)

    def isThreefoldRepetition(self):
        key = self._boardKey()
        return self.positionHistory.get(key, 0) >= 3