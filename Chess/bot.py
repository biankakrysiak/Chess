import random
import time

class EasyBot:
    def __init__(self, playAsWhite):
        self.playAsWhite = playAsWhite

    def getMove(self, gs):
        savedFlags = (gs.whiteKingMoved, gs.blackKingMoved,
                      gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                      gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                      gs.enPassantTarget)
        moves = gs.getValidMoves()
        # prefer checkmate
        for move in moves:
            gs.makeMove(move)
            if gs.checkmate:
                gs.undoMove()
                (gs.whiteKingMoved, gs.blackKingMoved,
                 gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                 gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                 gs.enPassantTarget) = savedFlags
                return move
            gs.undoMove()
            (gs.whiteKingMoved, gs.blackKingMoved,
             gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
             gs.blackKingsRookMoved, gs.blackQueensRookMoved,
             gs.enPassantTarget) = savedFlags

        def isSafe(move):
            # returns True if piece wont be hanging after move
            gs.makeMove(move)
            safe = not gs.isSquareAttacked(move.endRow, move.endCol, byWhite=not self.playAsWhite)
            gs.undoMove()
            (gs.whiteKingMoved, gs.blackKingMoved,
             gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
             gs.blackKingsRookMoved, gs.blackQueensRookMoved,
             gs.enPassantTarget) = savedFlags
            return safe

        # prefer safe captures with material gain
        good_captures = []
        for move in moves:
            if move.pieceCaptured != '--':
                captured_val = PIECE_VALUES.get(move.pieceCaptured[1], 0)
                moved_val    = PIECE_VALUES.get(move.pieceMoved[1], 0)
                if captured_val >= moved_val and isSafe(move):
                    good_captures.append((captured_val - moved_val, move))

        if good_captures and random.random() < 0.75:
            good_captures.sort(key=lambda x: -x[0])  # best capture first
            return good_captures[0][1]

        # prefer safe moves over hanging pieces
        safe_moves = [m for m in moves if isSafe(m)]
        pool = safe_moves if safe_moves else moves

        # prefer center control and development
        def scoreMove(move):
            score = 0
            r, c = move.endRow, move.endCol
            # center bonus
            score += max(0, 3 - abs(r - 3.5)) + max(0, 3 - abs(c - 3.5))
            # development bonus - move pieces off back rank
            if move.pieceMoved[1] in ('N', 'B'):
                score += 3
            return score

        if random.random() < 0.5:
            pool.sort(key=lambda m: -scoreMove(m))
            return pool[0]

        return random.choice(pool)

PIECE_VALUES = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 0}

PAWN_TABLE_W = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0],
]
PAWN_TABLE_B = PAWN_TABLE_W[::-1]

KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50],
]

BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20],
]

ROOK_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [0,  0,  0,  5,  5,  0,  0,  0],
]

QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [-5,   0,  5,  5,  5,  5,  0, -5],
    [0,    0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20],
]

KING_TABLE_MID = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [20,  20,  0,  0,  0,  0, 20, 20],
    [20,  30, 10,  0,  0, 10, 30, 20],
]
KING_TABLE_MID_B = KING_TABLE_MID[::-1]

TABLES_W = {'P': PAWN_TABLE_W, 'N': KNIGHT_TABLE, 'B': BISHOP_TABLE,
            'R': ROOK_TABLE,   'Q': QUEEN_TABLE,   'K': KING_TABLE_MID}
TABLES_B = {'P': PAWN_TABLE_B, 'N': KNIGHT_TABLE, 'B': BISHOP_TABLE,
            'R': ROOK_TABLE,   'Q': QUEEN_TABLE,   'K': KING_TABLE_MID_B}

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
    
    def evaluateBoard(self, gs):
        score = 0
        for r in range(8):
            for c in range(8):
                piece = gs.board[r][c]
                if piece == '--':
                    continue
                color    = piece[0]
                ptype    = piece[1]
                val      = PIECE_VALUES[ptype]
                table    = TABLES_W[ptype] if color == 'w' else TABLES_B[ptype]
                posBonus = table[r][c]
                if color == 'w':
                    score += val + posBonus
                else:
                    score -= val + posBonus
        return score

    def minimax(self, gs, depth, alpha, beta, maximizing):
        if depth == 0:
            return self.evaluateBoard(gs), None

        # save castling flags before searching
        savedFlags = (gs.whiteKingMoved, gs.blackKingMoved,
                      gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                      gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                      gs.enPassantTarget)

        moves = gs.getValidMoves()
        if not moves:
            if gs.checkmate:
                return (-99999 if maximizing else 99999), None
            return 0, None # stalemate

        bestMove = None
        if maximizing:
            maxEval = -float('inf')
            for move in moves:
                gs.makeMove(move)
                if move.promotionPending:
                    gs.board[move.endRow][move.endCol] = 'wQ'
                    move.promotionPiece = 'wQ'
                eval, _ = self.minimax(gs, depth - 1, alpha, beta, False)
                gs.undoMove()
                # restore flags after undo
                (gs.whiteKingMoved, gs.blackKingMoved,
                 gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                 gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                 gs.enPassantTarget) = savedFlags
                if eval > maxEval:
                    maxEval = eval
                    bestMove = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxEval, bestMove
        else:
            minEval = float('inf')
            for move in moves:
                gs.makeMove(move)
                if move.promotionPending:
                    gs.board[move.endRow][move.endCol] = 'bQ'
                    move.promotionPiece = 'bQ'
                eval, _ = self.minimax(gs, depth - 1, alpha, beta, True)
                gs.undoMove()
                # restore flags after undo
                (gs.whiteKingMoved, gs.blackKingMoved,
                 gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                 gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                 gs.enPassantTarget) = savedFlags
                if eval < minEval:
                    minEval = eval
                    bestMove = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval, bestMove

    def getMove(self, gs):
        maximizing = gs.whiteToMove
        _, move = self.minimax(gs, self.depth, -float('inf'), float('inf'), maximizing)
        return move
    
class HardBot:
    def __init__(self):
        pass