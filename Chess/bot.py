import random
import time

class EasyBot:
    def __init__(self, playAsWhite):
        self.playAsWhite = playAsWhite

    def getMove(self, gs):
        moves = gs.getValidMoves()
        if not moves:
            return None

        # prefer checkmate
        for move in moves:
            gs.makeMove(move)
            if gs.checkmate:
                gs.undoMove()
                return move
            gs.undoMove()

        # prefer captures with positive material gain (don't hang pieces)
        good_captures = []
        for move in moves:
            if move.pieceCaptured != '--':
                captured_val = PIECE_VALUES.get(move.pieceCaptured[1], 0)
                moved_val    = PIECE_VALUES.get(move.pieceMoved[1], 0)
                if captured_val >= moved_val:  # only if not losing material
                    good_captures.append(move)

        if good_captures and random.random() < 0.6:
            return random.choice(good_captures)

        return random.choice(moves)

PIECE_VALUES = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0}

def createBot(mode, playAsWhite):
    if mode == 'easy':
        return EasyBot(playAsWhite)
    elif mode == 'medium':
        return MediumBot(playAsWhite)
    elif mode == 'hard':
        return HardBot(playAsWhite)
    return None

class MediumBot:
    def __init__(self, playAsWhite):
        self.playAsWhite = playAsWhite
        self.depth = 3

class HardBot:
    def __init__(self):
        pass