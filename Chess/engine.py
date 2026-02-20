# Stores informations about current state of the game. 
# Shows valid moves. Keeps move logs.
from move import Move

class ChessEngine:
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR'],
             ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
             ['--', '--','--', '--','--', '--','--', '--'],
             ['--', '--','--', '--','--', '--','--', '--'],
             ['--', '--','--', '--','--', '--','--', '--'],
             ['--', '--','--', '--','--', '--','--', '--'],
             ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
             ['wR', 'wN', 'wB', 'wK', 'wQ', 'wB', 'wN', 'wR']
        ]
        self.whiteToMove = True
        self.moveLog = []
        
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
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
        
    def getRookMoves(self, r, c, moves):
        # generate all possible moves from position (r,c) for current player
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
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
                row = dr + row
                col = dc + col           

    def getBishopMoves(self, r, c, moves):
        directions = [(-1,-1), (-1,1), (1,-1), (1,1)]  # up-left, up-right, down-left, down-right
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
                row = dr + row
                col = dc + col    
    
    def getKnightMoves(self, r, c, moves):
        return 0
    
    def getQueenMoves(self, r, c, moves):
        return 0
    
    def getKingMoves(self, r, c, moves):
        return 0
