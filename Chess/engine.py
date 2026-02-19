# Stores informations about current state of the game. 
# Shows valid moves. Keeps move logs.
import move

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

