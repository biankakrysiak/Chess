import random
import time
import torch
import torch.nn as nn
import numpy as np
import chess
import os

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
    def orderMoves(self, moves, gs):
        # sort moves: captures first (MVV-LVA), then others
        def score(move):
            s = 0
            if move.pieceCaptured != '--':
                s += 10 * PIECE_VALUES.get(move.pieceCaptured[1], 0) - PIECE_VALUES.get(move.pieceMoved[1], 0)
            if move.promotionPending:
                s += 900
            return s
        return sorted(moves, key=score, reverse=True)
    
    def minimax(self, gs, depth, alpha, beta, maximizing):
        if depth == 0:
            return self.evaluateBoard(gs), None

        # save castling flags before searching
        savedFlags = (gs.whiteKingMoved, gs.blackKingMoved,
                      gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                      gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                      gs.enPassantTarget)

        moves = self.orderMoves(gs.getValidMoves(), gs)
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
    
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'modelTraining', 'chess_model_hard.pth')

class ChessNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(12, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64*8*8, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 64),     nn.ReLU(),
            nn.Linear(64, 1),       nn.Tanh()
        )
    def forward(self, x):
        return self.fc(self.conv(x)).squeeze(1)

def boardToTensor(board):
    planes = np.zeros((12, 8, 8), dtype=np.float32)
    piece_idx = {'P':0,'N':1,'B':2,'R':3,'Q':4,'K':5}
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            row = 7 - (sq // 8)
            col = sq % 8
            idx = piece_idx[piece.symbol().upper()]
            if piece.color == chess.WHITE:
                planes[idx][row][col] = 1.0
            else:
                planes[idx+6][row][col] = 1.0
    return planes

class HardBot:
    def __init__(self, playAsWhite):
        self.playAsWhite = playAsWhite
        self.depth = 4
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = ChessNet().to(self.device)
        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=self.device))
        self.model.eval()

    def gsToCBoard(self, gs):
        board = chess.Board()
        board.clear()
        piece_map = {'P': chess.PAWN,   'N': chess.KNIGHT, 'B': chess.BISHOP,
                     'R': chess.ROOK,   'Q': chess.QUEEN,  'K': chess.KING}
        for r in range(8):
            for c in range(8):
                p = gs.board[r][c]
                if p != '--':
                    sq    = chess.square(c, 7 - r)
                    color = chess.WHITE if p[0] == 'w' else chess.BLACK
                    board.set_piece_at(sq, chess.Piece(piece_map[p[1]], color))
        board.turn = chess.WHITE if gs.whiteToMove else chess.BLACK
        return board

    def evaluateBoard(self, gs):
        board  = self.gsToCBoard(gs)
        tensor = torch.tensor(boardToTensor(board)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            score = self.model(tensor).item()
        return int(score * 10000)

    def orderMoves(self, moves):
        def score(move):
            s = 0
            if move.pieceCaptured != '--':
                s += 10 * PIECE_VALUES.get(move.pieceCaptured[1], 0) \
                        -      PIECE_VALUES.get(move.pieceMoved[1], 0)
            if move.promotionPending:
                s += 900
            return s
        return sorted(moves, key=score, reverse=True)

    def minimax(self, gs, depth, alpha, beta, maximizing):
        if depth == 0:
            return self.evaluateBoard(gs), None

        savedFlags = (gs.whiteKingMoved, gs.blackKingMoved,
                      gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                      gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                      gs.enPassantTarget)

        moves = self.orderMoves(gs.getValidMoves())
        if not moves:
            if gs.checkmate:
                return (-99999 if maximizing else 99999), None
            return 0, None

        bestMove = None
        if maximizing:
            maxEval = -float('inf')
            for move in moves:
                gs.makeMove(move)
                if move.promotionPending:
                    gs.board[move.endRow][move.endCol] = 'wQ'
                    move.promotionPiece = 'wQ'
                eval, _ = self.minimax(gs, depth-1, alpha, beta, False)
                gs.undoMove()
                (gs.whiteKingMoved, gs.blackKingMoved,
                 gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                 gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                 gs.enPassantTarget) = savedFlags
                if eval > maxEval:
                    maxEval, bestMove = eval, move
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
                eval, _ = self.minimax(gs, depth-1, alpha, beta, True)
                gs.undoMove()
                (gs.whiteKingMoved, gs.blackKingMoved,
                 gs.whiteKingsRookMoved, gs.whiteQueensRookMoved,
                 gs.blackKingsRookMoved, gs.blackQueensRookMoved,
                 gs.enPassantTarget) = savedFlags
                if eval < minEval:
                    minEval, bestMove = eval, move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minEval, bestMove

    def getMove(self, gs):
        maximizing = gs.whiteToMove
        _, move = self.minimax(gs, self.depth, -float('inf'), float('inf'), maximizing)
        return move