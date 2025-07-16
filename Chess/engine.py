# Stores informations about current state of the game. 
# Shows valid moves. Keeps move logs.

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

