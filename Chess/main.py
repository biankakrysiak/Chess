# Handles user input and shows current position (Game state)

import pygame as p
import engine

WIDTH = 512
HEIGHT = 512
DIMENSION = 8
SQR_SIZE = HEIGHT // DIMENSION
fps = 15  # animations tbd
IMAGES = {}

def loadImages():
    pieces = ['wR', 'wN', 'wB', 'wK', 'wQ', 'wP', 'bR', 'bN', 'bB', 'bK', 'bQ', 'bP']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/img/" + piece + ".png"), (SQR_SIZE, SQR_SIZE))
        #IMAGES[piece] = p.image.load("Chess/img/" + piece + ".png")

def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.ChessEngine()
    print(gs.board)
    loadImages()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            drawGameState(screen, gs)
            clock.tick(fps)
            p.display.flip()
            

def drawGameState(screen, gs):
    drawBoard(screen)
    # add highlights or move suggestions
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQR_SIZE, r*SQR_SIZE, SQR_SIZE, SQR_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQR_SIZE, r*SQR_SIZE, SQR_SIZE, SQR_SIZE))

if __name__ == "__main__":
    main()
