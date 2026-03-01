# prepare_data.py
import chess
import chess.pgn
import numpy as np
import os
import io

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
                planes[idx + 6][row][col] = 1.0
    return planes

def parsePGNFolder(folder, output_file, min_elo=2200, max_games=20000, chunk_size=100000):
    positions = []
    labels    = []
    game_count = 0
    chunk_num  = 0

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith('.pgn'):
            continue
        print(f"Parsing {filename}...")
        with open(os.path.join(folder, filename), encoding='utf-8', errors='ignore') as f:
            while True:
                try:
                    game = chess.pgn.read_game(f)
                except Exception:
                    break
                if game is None:
                    break

                try:
                    w_elo = int(game.headers.get('WhiteElo', 0))
                    b_elo = int(game.headers.get('BlackElo', 0))
                except:
                    continue
                if w_elo < min_elo or b_elo < min_elo:
                    continue
                if game.headers.get('Termination') == 'Time forfeit':
                    continue

                result = game.headers.get('Result')
                if result == '1-0':        label =  1.0
                elif result == '0-1':      label = -1.0
                elif result == '1/2-1/2':  label =  0.0
                else: continue

                board = game.board()
                move_num = 0
                for move in game.mainline_moves():
                    board.push(move)
                    move_num += 1
                    if move_num < 5:
                        continue
                    positions.append(boardToTensor(board))
                    labels.append(label)

                game_count += 1
                if game_count % 1000 == 0:
                    print(f"  {game_count} games, {len(positions)} positions")

                # save chunk and free memory
                if len(positions) >= chunk_size:
                    np.save(f"{output_file}_X_{chunk_num}.npy", np.array(positions, dtype=np.float32))
                    np.save(f"{output_file}_y_{chunk_num}.npy", np.array(labels,    dtype=np.float32))
                    print(f"  -> saved chunk {chunk_num}")
                    chunk_num += 1
                    positions = []
                    labels    = []

                if game_count >= max_games:
                    break

        if game_count >= max_games:
            break

    # save remaining
    if positions:
        np.save(f"{output_file}_X_{chunk_num}.npy", np.array(positions, dtype=np.float32))
        np.save(f"{output_file}_y_{chunk_num}.npy", np.array(labels,    dtype=np.float32))
        chunk_num += 1

    print(f"Saved {chunk_num} chunks from {game_count} games")

    positions = np.array(positions, dtype=np.float32)
    labels    = np.array(labels,    dtype=np.float32)
    np.save(output_file + '_X.npy', positions)
    np.save(output_file + '_y.npy', labels)
    print(f"Saved {len(positions)} positions from {game_count} games")

parsePGNFolder('pgn_data', 'dataset', min_elo=2200, max_games=20000)