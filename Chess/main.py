# Handles user input and shows current position (Game state)
import pygame as p # type: ignore
import engine
from move import Move

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
    #print(gs.board)
    loadImages()
    selected = None
    validMoves = []
    running = True
    moveNr = 1
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                x, y = e.pos
                col = x // SQR_SIZE
                row = y // SQR_SIZE

                # first click
                if selected is None: 
                    if gs.board[row][col] != '--':
                        piece = gs.board[row][col]
                        if (gs.whiteToMove and piece[0] == 'w') or (not gs.whiteToMove and piece[0] == 'b'):
                            selected = (row, col)
                            validMoves = gs.getValidMoves()

                else:
                    if selected == (row, col):
                        selected = None
                        validMoves = []
                    else:
                        #validMoves = gs.getValidMoves()
                        clickedMove = None
                        for m in validMoves:
                            if m.startRow == selected[0] and m.startCol == selected[1] and \
                               m.endRow == row and m.endCol == col:
                                clickedMove = m
                                break
                        if clickedMove:
                            gs.makeMove(clickedMove)
                            if clickedMove.promotionPending:
                                promotionPiece = choosePromotion(screen, clickedMove, gs.whiteToMove)
                                gs.board[clickedMove.endRow][clickedMove.endCol] = promotionPiece
                            print(clickedMove)

                            validMoves = gs.getValidMoves()
                            if gs.checkmate:
                                print("Checkmate")
                            elif gs.stalemate:
                                print("Stalemate")

                        selected = None
                        validMoves = []

            drawGameState(screen, gs, selected, validMoves)
            clock.tick(fps)
            p.display.flip()
            #print(gs.board)
            #print(gs.moveLog)
            

def drawGameState(screen, gs, selected, validMoves):
    drawBoard(screen)
    drawHighlights(screen, gs, selected, validMoves)
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

def choosePromotion(screen, move, whiteToMove):
    row, col = move.endRow, move.endCol
    squareX = col * SQR_SIZE
    squareY = row * SQR_SIZE
    
    pieces = ["Q", "R", "B", "N"]
    color = "b" if whiteToMove else "w"
   
    rects = []
    for i, pType in enumerate(pieces):
        r = i // 2  # row 0 or 1
        c = i % 2   # column 0 or 1
        rectWidth = SQR_SIZE // 2
        rectHeight = SQR_SIZE // 2
        rectX = squareX + c * rectWidth
        rectY = squareY + r * rectHeight
        rect = p.Rect(rectX, rectY, rectWidth, rectHeight)
        img = p.transform.scale(IMAGES[color+pType], (rectWidth, rectHeight))
        screen.blit(img, rect)
        rects.append((rect, color+pType))
    p.display.flip()
    
    choosing = True
    while choosing:
        for e in p.event.get():
            if e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                x, y = e.pos
                for rect, piece in rects:
                    if rect.collidepoint(x, y):
                        return piece

def drawHighlights(screen, gs, selected, validMoves):
    if gs.whiteToMove:
        kr, kc = gs.whiteKingPos
    else:
        kr, kc = gs.blackKingPos
    
    if gs.isSquareAttacked(kr, kc, byWhite=not gs.whiteToMove):
        layers = [
            (0, (200, 60, 60, 160)),
            (1, (220, 90, 90, 110)),
            (2, (240, 120, 120, 60)),
            (3, (255, 150, 150, 25)),
        ]
        for offset, (r, g, b, a) in layers:
            s = p.Surface((SQR_SIZE - offset*2, SQR_SIZE - offset*2), p.SRCALPHA)
            p.draw.rect(s, (r, g, b, a), s.get_rect(), 3)
            screen.blit(s, (kc * SQR_SIZE + offset, kr * SQR_SIZE + offset))

    
    if selected is None:
        return
    
    dotColor = p.Color(100, 100, 100, 100)
    cornerColor = p.Color(100, 100, 100)
    cornerSize = SQR_SIZE // 6
    m = 1
    
    for move in validMoves:
        if move.startRow == selected[0] and move.startCol == selected[1]:
            col = move.endCol
            row = move.endRow
            x = col * SQR_SIZE
            y = row * SQR_SIZE
            w = SQR_SIZE - 2 * m
            centerX = col * SQR_SIZE + SQR_SIZE // 2
            centerY = row * SQR_SIZE + SQR_SIZE // 2
            if gs.board[row][col] == '--':
                p.draw.circle(screen, dotColor, (centerX, centerY), SQR_SIZE // 6)
            else:
                # left up
                p.draw.polygon(screen, cornerColor, [(x, y), (x + cornerSize, y), (x, y + cornerSize)])
                # right up
                p.draw.polygon(screen, cornerColor, [(x + w, y), (x + w - cornerSize, y), (x + w, y + cornerSize)])
                # left down
                p.draw.polygon(screen, cornerColor, [(x, y + w), (x + cornerSize, y + w), (x, y + w - cornerSize)])
                # right down
                p.draw.polygon(screen, cornerColor, [(x + w, y + w), (x + w - cornerSize, y + w), (x + w, y + w - cornerSize)])

if __name__ == "__main__":
    main()
