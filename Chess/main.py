# Handles user input and shows current position (Game state)
import pygame as p # type: ignore
import engine
from move import Move

WIDTH = 512
HEIGHT = 512
PANEL_WIDTH = 220
DIMENSION = 8
SQR_SIZE = HEIGHT // DIMENSION
HEADER_HEIGHT = 35
LINE_HEIGHT = 22
VISIBLE_LINES = (HEIGHT - HEADER_HEIGHT)//LINE_HEIGHT
fps = 15  # animations tbd
IMAGES = {}

def loadImages():
    pieces = ['wR', 'wN', 'wB', 'wK', 'wQ', 'wP', 'bR', 'bN', 'bB', 'bK', 'bQ', 'bP']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/img/" + piece + ".png"), (SQR_SIZE, SQR_SIZE))
        #IMAGES[piece] = p.image.load("Chess/img/" + piece + ".png")

def main():
    p.init()
    screen = p.display.set_mode((WIDTH + PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.ChessEngine()
    #print(gs.board)
    loadImages()
    selected = None
    validMoves = []
    running = True
    moveHistory = []
    scrollOffset = 0
    scrollDragging = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEWHEEL:
                total_lines = (len(moveHistory) + 1) // 2
                scrollOffset -= e.y
                scrollOffset = max(0, min(scrollOffset, total_lines - VISIBLE_LINES))
            elif e.type == p.MOUSEBUTTONUP and e.button == 1:
                scrollDragging = False
            elif e.type == p.MOUSEMOTION:
                if scrollDragging:
                    x, y = e.pos
                    total_lines = (len(moveHistory) + 1) // 2
                    if total_lines > VISIBLE_LINES:
                        track_height = HEIGHT - HEADER_HEIGHT
                        ratio = (y - HEADER_HEIGHT) / track_height
                        scrollOffset = int(ratio * total_lines)
                        scrollOffset = max(0, min(scrollOffset, total_lines - VISIBLE_LINES))
            elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                x, y = e.pos
                if x >= WIDTH + PANEL_WIDTH - 12:  # scrollbar click
                    scrollDragging = True
                    continue
                if x >= WIDTH:
                    continue
                col = x // SQR_SIZE
                row = y // SQR_SIZE
                if row < 0 or row >= DIMENSION or col < 0 or col >= DIMENSION:
                    continue

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

                            validMoves = gs.getValidMoves()
                            notation = gs.getMoveNotation(clickedMove)
                            moveHistory.append(notation)
                            scrollOffset = max(0, (len(moveHistory)+1) // 2- VISIBLE_LINES)
                            
                            if gs.checkmate:
                                print(buildPGN(moveHistory))
                                print("Checkmate")
                            elif gs.stalemate:
                                print(buildPGN(moveHistory))
                                print("Stalemate")

                        selected = None
                        validMoves = []

            drawGameState(screen, gs, selected, validMoves)
            drawPanel(screen, moveHistory, scrollOffset)
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

def buildPGN(moveHistory):
    pgn = ''
    for i, move in enumerate(moveHistory):
        if i % 2 == 0:
            pgn += f"{i//2+1}. {move} "
        else:
            pgn += f"{move} "
    return pgn.strip()

def drawPanel(screen, moveHistory, scrollOffset):
    panelX = WIDTH
    p.draw.rect(screen, p.Color(50, 50, 50), p.Rect(panelX, 0, PANEL_WIDTH, HEIGHT))
    
    font = p.font.SysFont('consolas', 15)
    x_white = panelX + 35
    x_black = panelX + PANEL_WIDTH // 2 + 10

    header = font.render('Move History', True, p.Color(200, 200, 200))
    screen.blit(header, (panelX + PANEL_WIDTH//2 - header.get_width()//2, 10))

    total_lines = (len(moveHistory) + 1) // 2
    scrollOffset = max(0, min(scrollOffset, total_lines - VISIBLE_LINES))

    for i in range(VISIBLE_LINES):
        lineNr = scrollOffset + i
        if lineNr >= total_lines:
            break

        moveNr = lineNr + 1
        moveIdx = lineNr * 2
        y = HEADER_HEIGHT + i * LINE_HEIGHT

        nr = font.render(f"{moveNr}.", True, p.Color(150, 150, 150))
        screen.blit(nr, (panelX + 5, y))

        white = font.render(moveHistory[moveIdx], True, p.Color(255, 255, 255))
        screen.blit(white, (x_white, y))

        if moveIdx + 1 < len(moveHistory):
            black = font.render(moveHistory[moveIdx + 1], True, p.Color(200, 200, 200))
            screen.blit(black, (x_black, y))

    # scrollbar
    if total_lines > VISIBLE_LINES:
        track_x = panelX + PANEL_WIDTH - 10
        track_height = HEIGHT - HEADER_HEIGHT
        p.draw.rect(screen, p.Color(60, 60, 60), p.Rect(track_x, HEADER_HEIGHT, 8, track_height))

        thumb_ratio = VISIBLE_LINES / total_lines
        thumb_height = max(20, int(track_height * thumb_ratio))
        thumb_pos = HEADER_HEIGHT + int((scrollOffset / total_lines) * track_height)
        p.draw.rect(screen, p.Color(150, 150, 150), p.Rect(track_x, thumb_pos, 8, thumb_height), border_radius=4)

if __name__ == "__main__":
    main()
