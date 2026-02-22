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
        
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

        # update king rook moved flags, for castling
        if move.pieceMoved == 'wK':
            self.whiteKingMoved = True
        elif move.pieceMoved == 'bK':
            self.blackKingMoved = True
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
            
        
        self.whiteToMove = not self.whiteToMove

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
        self.getCastleMoves(r, c, moves)

    def getCastleMoves(self, r, c, moves):
        if self.whiteToMove:
            if not self.whiteKingMoved:
                # Kingside
                if not self.whiteKingsRookMoved and self.board[7][5] == "--" and self.board[7][6] == "--":
                    moves.append(Move((7, 4), (7, 6), self.board))  # king moves 2 squares
                # Queenside
                if not self.whiteQueensRookMoved and self.board[7][1] == "--" and self.board[7][2] == "--" and self.board[7][3] == "--":
                    moves.append(Move((7, 4), (7, 2), self.board))
        else:
            if not self.blackKingMoved:
                # Kingside
                if not self.blackKingsRookMoved and self.board[0][5] == "--" and self.board[0][6] == "--":
                    moves.append(Move((0, 4), (0, 6), self.board))
                # Queenside
                if not self.blackQueensRookMoved and self.board[0][1] == "--" and self.board[0][2] == "--" and self.board[0][3] == "--":
                    moves.append(Move((0, 4), (0, 2), self.board))