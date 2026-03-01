# Chess

A fully featured chess game built with Python and Pygame, with three bot difficulty modes including an experimental ML-powered opponent.

## Features

- **Full chess rules** - castling, en passant, pawn promotion, check/checkmate/stalemate, threefold repetiton
- **Algebraic notation** - full move history with check (`+`) and checkmate (`#`) symbols
- **Move history panel** - scrollable, with navigation arrows to replay any position
- **Clocks** - configurable time controls with increment (Bullet, Blitz, Rapid, Classical)
- **Board flip** - play as white or black, or random
- **PGN export** - save games in standard PGN format, compatible with Lichess and other tools
- **Three bot difficulties** (vs human only)
- **Local multiplayer** - pass-and-play with draw offer system

## Project Structure

```
Chess/
├── main.py            # Pygame UI, event loop, rendering
├── engine.py          # Game logic, move validation, check detection
├── move.py            # Move class, algebraic notation generation
├── menu.py            # Main menu (mode, time control, color selection)
├── bot.py             # Bot implementations (Easy, Medium, Hard)
├── img/               # Piece images (wP, bK, ...)
└── modelTraining/
    ├── chess_model_hard.pth   # Trained neural network weights
    ├── prepareData.py         # PGN -> numpy dataset
    └── train.py               # Model training script
```

## Requirements

```
pygame
torch
numpy
chess
tqdm
```

Install with:

```bash
pip install pygame torch numpy chess tqdm
```

## Running

```bash
python Chess/main.py
```

## Bot Difficulty Modes

### Easy
Heuristic-based bot. Prefers checkmates, avoids hanging pieces, prefers captures where material is equal or better, and plays towards the center. Deliberately imperfect - occasionally plays random moves. 

### Medium
Searches 3 moves ahead using minimax - tries all possible continuations and picks the best one.
Uses alpha-beta pruning to skip branches that can't affect the result, making the search fast enough to run in real time.
Positions are scored by material count plus bonuses for piece placement (for example, knights in the center score higher than knights on the edge).
Captures are evaluated first to cut off bad lines earlier.

### Hard

The Hard bot uses a small convolutional neural network (`ChessNet`) trained to predict game outcome (+1 white wins, -1 black wins) from board position. It's plugged into a depth-4 minimax search as the evaluation function instead of hand-crafted piece values.

Currently trained on a limited dataset (~79 PGN files, blitz games, 2200+ elo) due to hardware constraints - the model has no opening book, limited tactical awareness, and in practice plays weaker than Medium. Retraining on a larger dataset would significantly improve its strength.

**To retrain with more data:**
1. Add PGN files to `Chess/modelTraining/pgn_data/`
2. Run `prepareData.py` to generate dataset chunks
3. Run `train.py` - saves best model as `chess_model_hard.pth`
4. The architecture in `train.py` and `bot.py` (`ChessNet` class) **must be identical** - mismatches will cause a runtime error

## Time Controls

| Label  | Time   | Increment | Category  |
|--------|--------|-----------|-----------|
| 1+0    | 1 min  | 0 sec     | Bullet    |
| 1+1    | 1 min  | 1 sec     | Bullet    |
| 3+0    | 3 min  | 0 sec     | Blitz     |
| 3+2    | 3 min  | 2 sec     | Blitz     |
| 5+0    | 5 min  | 0 sec     | Blitz     |
| 10+0   | 10 min | 0 sec     | Rapid     |
| 15+10  | 15 min | 10 sec    | Rapid     |
| 30+0   | 30 min | 0 sec     | Classical |

