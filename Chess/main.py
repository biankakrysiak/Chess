# Handles user input and shows current position (Game state)
import pygame as p # type: ignore
import os
from datetime import datetime
import engine
from move import Move
import menu
from bot import createBot
import random

WIDTH = 512
HEIGHT = 512
PANEL_WIDTH = 220
DIMENSION = 8
SQR_SIZE = HEIGHT // DIMENSION
HEADER_HEIGHT = 35
LINE_HEIGHT = 22
VISIBLE_LINES = (HEIGHT - HEADER_HEIGHT)//LINE_HEIGHT
fps = 60  
IMAGES = {}

def loadImages():
    pieces = ['wR', 'wN', 'wB', 'wK', 'wQ', 'wP', 'bR', 'bN', 'bB', 'bK', 'bQ', 'bP']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/img/" + piece + ".png"), (SQR_SIZE, SQR_SIZE))
        #IMAGES[piece] = p.image.load("Chess/img/" + piece + ".png")

def main():
    p.init()
    settings = menu.main()
    
    screen = p.display.set_mode((WIDTH + PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.ChessEngine()
    #print(gs.board)
    loadImages()
    selected = None
    validMoves = []
    moveHistory = []
    scrollOffset = 0
    scrollDragging = False
    gameOverResult = None # {'winner': 'White'/'Black'/'Draw', 'reason': str}
    showGameOver = False
    viewIndex = 0  # 0 = start, len(moveLog) = current
    viewMode  = False

    def triggerGameOver(winner, reason):
        nonlocal gameOver, gameOverResult, showGameOver
        gameOver = True
        gameOverResult = {'winner': winner, 'reason': reason}
        showGameOver = True

    mode = settings['mode']
    baseTime = settings['baseTime']
    increment = settings['increment']
    
    playerIsWhite = True
    if settings['color'] == 'black':
        playerIsWhite = False
    elif settings['color'] == 'random':
        import random
        playerIsWhite = random.choice([True, False])

    flipped = not playerIsWhite
    whiteTime = float(baseTime)
    blackTime = float(baseTime)
    lastTick = p.time.get_ticks()
    gameOver = False
    showDrawOffer = False

    bot = None
    if mode in ('easy', 'medium', 'hard'):
        botIsWhite = not playerIsWhite
        bot = createBot(mode, botIsWhite)
    botMoveTime = None

    running = True
    while running:
        # tick clock
        now = p.time.get_ticks()
        dt = (now - lastTick) / 1000.0
        lastTick = now
        if not gameOver:
            if gs.whiteToMove:
                whiteTime -= dt
                if whiteTime <= 0:
                    whiteTime = 0
                    triggerGameOver('Black', 'on time')
            else:
                blackTime -= dt
                if blackTime <= 0:
                    blackTime = 0
                    triggerGameOver('White', 'on time')
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEWHEEL:
                total_lines = len(moveHistory)
                scrollOffset -= e.y
                scrollOffset = max(0, min(scrollOffset, total_lines - VISIBLE_LINES))
            
            elif e.type == p.MOUSEBUTTONUP and e.button == 1:
                scrollDragging = False
            
            elif e.type == p.MOUSEMOTION:
                if scrollDragging:
                    x, y = e.pos
                    total_lines = len(moveHistory)
                    if total_lines > VISIBLE_LINES:
                        track_height = HEIGHT - HEADER_HEIGHT
                        ratio = (y - HEADER_HEIGHT) / track_height
                        scrollOffset = int(ratio * total_lines)
                        scrollOffset = max(0, min(scrollOffset, total_lines - VISIBLE_LINES))
            
            elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                x, y = e.pos

                if showDrawOffer:
                    acceptRect, declineRect, _ = drawDrawOfferPopup(screen, gs, flipped)
                    if acceptRect.collidepoint(x, y):
                        showDrawOffer = False
                        triggerGameOver('Draw', 'by agreement')
                    elif declineRect.collidepoint(x, y):
                        showDrawOffer = False
                    continue
                
                if showGameOver:
                    popupW, popupH = 320, 140
                    popupX = (WIDTH - popupW) // 2
                    popupY = (HEIGHT - popupH) // 2
                    closeSize = 20
                    closeRect = p.Rect(popupX + popupW - closeSize - 8, popupY + 8, closeSize, closeSize)
                    if closeRect.collidepoint(x, y):
                        showGameOver = False
                    continue

                if x >= WIDTH + PANEL_WIDTH - 12:  # scrollbar click
                    scrollDragging = True
                    continue
                if x >= WIDTH:
                    navRects, actionRects = drawPanel(screen, gs, moveHistory, scrollOffset, whiteTime, blackTime, flipped, gameOver)
                    
                    if navRects.get('start') and navRects['start'].collidepoint(x, y):
                        viewIndex = 0
                        viewMode  = True
                    elif navRects.get('back') and navRects['back'].collidepoint(x, y):
                        viewIndex = max(0, viewIndex - 1)
                        viewMode  = viewIndex < len(gs.moveLog)
                    elif navRects.get('fwd') and navRects['fwd'].collidepoint(x, y):
                        viewIndex = min(len(gs.moveLog), viewIndex + 1)
                        viewMode  = viewIndex < len(gs.moveLog)
                    elif navRects.get('end') and navRects['end'].collidepoint(x, y):
                        viewIndex = len(gs.moveLog)
                        viewMode  = False
                    
                    if not gameOver:
                        if actionRects.get('resign') and actionRects['resign'].collidepoint(x, y):
                            winner = 'Black' if gs.whiteToMove else 'White'
                            triggerGameOver(winner, 'by resignation')
                        elif actionRects.get('draw') and actionRects['draw'].collidepoint(x, y):
                            if mode == 'local':
                                showDrawOffer = True
                                #triggerGameOver('Draw', 'by agreement')
                    else:
                        if actionRects.get('menu') and actionRects['menu'].collidepoint(x, y):
                            running = False
                            main()
                            return
                        elif actionRects.get('save') and actionRects['save'].collidepoint(x, y):
                            savePGN(moveHistory, gameOverResult, settings)
                    continue
                
                if gameOver:
                    continue
                
                col = x // SQR_SIZE
                row = y // SQR_SIZE
                if flipped:
                    col = 7 - col
                    row = 7 - row

                if row < 0 or row >= DIMENSION or col < 0 or col >= DIMENSION:
                    continue

                # first click
                if selected is None:
                    if gs.board[row][col] != '--':
                        piece = gs.board[row][col]
                        if mode == 'local':
                            canMove = (gs.whiteToMove and piece[0] == 'w') or (not gs.whiteToMove and piece[0] == 'b')
                        else:
                            canMove = (gs.whiteToMove == playerIsWhite) and \
                                      ((playerIsWhite and piece[0] == 'w') or (not playerIsWhite and piece[0] == 'b'))
                        if canMove:
                            selected = (row, col)
                            validMoves = gs.getValidMoves()

                else:
                    if selected == (row, col):
                        selected = None
                        validMoves = []
                    else:
                        clickedMove = None
                        for m in validMoves:
                            if m.startRow == selected[0] and m.startCol == selected[1] and \
                               m.endRow == row and m.endCol == col:
                                clickedMove = m
                                break
                        if clickedMove:
                            gs.makeMove(clickedMove)
                            if gs.whiteToMove:
                                blackTime += increment
                            else:
                                whiteTime += increment

                            if clickedMove.promotionPending:
                                promotionPiece = choosePromotion(screen, clickedMove, gs.whiteToMove, flipped)
                                gs.board[clickedMove.endRow][clickedMove.endCol] = promotionPiece
                                clickedMove.promotionPiece = promotionPiece
                            notation = gs.getMoveNotation(clickedMove)
                            moveHistory.append(notation)
                            
                            validMoves = gs.getValidMoves()
                            viewIndex = len(gs.moveLog)
                            viewMode  = False
                            scrollOffset = max(0, (len(moveHistory)+1) // 2- VISIBLE_LINES)
                            
                            if gs.checkmate:
                                if moveHistory:
                                    last = moveHistory[-1]
                                    if not last.endswith('#'):
                                        moveHistory[-1] = last.rstrip('+') + '#'
                                print(buildPGN(moveHistory))
                                print("Checkmate")
                                winner = 'Black' if gs.whiteToMove else 'White'
                                triggerGameOver(winner, 'by checkmate')
                            elif gs.stalemate:
                                print(buildPGN(moveHistory))
                                print("Stalemate")
                                triggerGameOver('Draw', 'by stalemate')

                        selected = None
                        validMoves = []
            # bot move
            if not gameOver and bot is not None:
                if gs.whiteToMove == bot.playAsWhite:
                    now = p.time.get_ticks()
                    if botMoveTime is None:
                        botMoveTime = now + random.randint(200, 400)
                    elif now >= botMoveTime:
                        botMoveTime = None
                        botMove = bot.getMove(gs)
                        if botMove:
                            gs.makeMove(botMove)
                            if gs.whiteToMove:
                                blackTime += increment
                            else:
                                whiteTime += increment
                            if botMove.promotionPending and not botMove.promotionPiece:
                                color = 'b' if not gs.whiteToMove else 'w'
                                gs.board[botMove.endRow][botMove.endCol] = color + 'Q'
                                botMove.promotionPiece = color + 'Q'
                            notation = gs.getMoveNotation(botMove)
                            moveHistory.append(notation)
                            validMoves = gs.getValidMoves()
                            viewIndex = len(gs.moveLog)
                            scrollOffset = max(0, (len(moveHistory)+1) // 2 - VISIBLE_LINES)
                            if gs.checkmate:
                                if moveHistory:
                                    last = moveHistory[-1]
                                    if not last.endswith('#'):
                                        moveHistory[-1] = last.rstrip('+') + '#'
                                winner = 'Black' if gs.whiteToMove else 'White'
                                triggerGameOver(winner, 'by checkmate')
                            elif gs.stalemate:
                                triggerGameOver('Draw', 'by stalemate')
                else:
                    botMoveTime = None 

        if viewMode:
            displayBoard = gs.getBoardAtMove(viewIndex)
            displayLog   = gs.moveLog[:viewIndex]
        else:
            displayBoard = gs.board
            displayLog   = gs.moveLog

        drawBoard(screen, flipped)
        if displayLog:
            lastMove = displayLog[-1]
            def sq(r, c):
                dr = 7 - r if flipped else r
                dc = 7 - c if flipped else c
                return dr, dc
            for r, c in [(lastMove.startRow, lastMove.startCol), (lastMove.endRow, lastMove.endCol)]:
                dr, dc = sq(r, c)
                s = p.Surface((SQR_SIZE, SQR_SIZE), p.SRCALPHA)
                s.fill((200, 168, 75, 50))
                screen.blit(s, (dc * SQR_SIZE, dr * SQR_SIZE))
        if not viewMode:
            drawHighlights(screen, gs, selected, validMoves, flipped)
        drawPieces(screen, displayBoard, flipped)
        drawCoordinates(screen, flipped)
        drawPanel(screen, gs, moveHistory, scrollOffset, whiteTime, blackTime, flipped, gameOver, viewIndex)
        if showDrawOffer:
            drawDrawOfferPopup(screen, gs, flipped)
        if showGameOver and gameOverResult:
            drawGameOverPopup(screen, gameOverResult)
        clock.tick(fps)
        p.display.flip()

def drawBoard(screen, flipped=False):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            dr = 7 - r if flipped else r
            dc = 7 - c if flipped else c
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(dc * SQR_SIZE, dr * SQR_SIZE, SQR_SIZE, SQR_SIZE))

def drawPieces(screen, board, flipped=False):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                dr = 7 - r if flipped else r
                dc = 7 - c if flipped else c
                screen.blit(IMAGES[piece], p.Rect(dc * SQR_SIZE, dr * SQR_SIZE, SQR_SIZE, SQR_SIZE))

def choosePromotion(screen, move, whiteToMove, flipped=False):
    row, col = move.endRow, move.endCol
    
    dr = 7 - row if flipped else row
    dc = 7 - col if flipped else col
    
    squareX = dc * SQR_SIZE
    squareY = dr * SQR_SIZE
    
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

def drawHighlights(screen, gs, selected, validMoves, flipped=False):
    def sq(r, c):  # convert board coords to screen coords
        dr = 7 - r if flipped else r
        dc = 7 - c if flipped else c
        return dr, dc
    
    # highlight last move
    if gs.moveLog:
        lastMove = gs.moveLog[-1]
        for r, c in [(lastMove.startRow, lastMove.startCol), (lastMove.endRow, lastMove.endCol)]:
            dr, dc = sq(r, c)
            s = p.Surface((SQR_SIZE, SQR_SIZE), p.SRCALPHA)
            s.fill((200, 168, 75, 50))
            screen.blit(s, (dc * SQR_SIZE, dr * SQR_SIZE))

    if gs.whiteToMove:
        kr, kc = gs.whiteKingPos
    else:
        kr, kc = gs.blackKingPos

    if gs.isSquareAttacked(kr, kc, byWhite=not gs.whiteToMove):
        dr, dc = sq(kr, kc)
        layers = [
            (0, (200, 60, 60, 160)),
            (1, (220, 90, 90, 110)),
            (2, (240, 120, 120, 60)),
            (3, (255, 150, 150, 25)),
        ]
        for offset, (r, g, b, a) in layers:
            s = p.Surface((SQR_SIZE - offset*2, SQR_SIZE - offset*2), p.SRCALPHA)
            p.draw.rect(s, (r, g, b, a), s.get_rect(), 3)
            screen.blit(s, (dc * SQR_SIZE + offset, dr * SQR_SIZE + offset))

    if selected is None:
        return

    dotColor   = p.Color(100, 100, 100, 100)
    cornerColor = p.Color(100, 100, 100)
    cornerSize  = SQR_SIZE // 6
    m = 1

    for move in validMoves:
        if move.startRow == selected[0] and move.startCol == selected[1]:
            dr, dc = sq(move.endRow, move.endCol)
            x = dc * SQR_SIZE
            y = dr * SQR_SIZE
            w = SQR_SIZE - 2 * m
            centerX = x + SQR_SIZE // 2
            centerY = y + SQR_SIZE // 2
            if gs.board[move.endRow][move.endCol] == '--':
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

def drawPanel(screen, gs, moveHistory, scrollOffset, whiteTime=None, blackTime=None, flipped=False, gameOver=False, viewIndex=None):
    panelX = WIDTH
    p.draw.rect(screen, p.Color(50, 50, 50), p.Rect(panelX, 0, PANEL_WIDTH, HEIGHT))

    font      = p.font.SysFont('consolas', 13)
    fontClock = p.font.SysFont('consolas', 14, bold=True)

    def formatTime(secs):
        secs = max(0, int(secs))
        m, s = divmod(secs, 60)
        return f"{m:02}:{s:02}"

    btnFont = p.font.SysFont('consolas', 9, bold=True)
    btnH    = 22
    btnW    = (PANEL_WIDTH - 20) // 4

    # buttons at bottom
    btnY2   = HEIGHT - btnH - 6
    actionRects = {}
    if not gameOver:
        activeBtns = [('Resign', 'resign'), ('Draw', 'draw')]
        bw2 = (PANEL_WIDTH - 20) // 2
        for i, (label, key) in enumerate(activeBtns):
            bx   = panelX + 5 + i * (bw2 + 10)
            rect = p.Rect(bx, btnY2, bw2, btnH)
            actionRects[key] = rect
            p.draw.rect(screen, p.Color(65, 65, 65), rect, border_radius=3)
            p.draw.rect(screen, p.Color(160, 135, 65), rect, width=1, border_radius=3)
            lbl = btnFont.render(label, True, p.Color(200, 168, 75))
            screen.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))
    else:
        activeBtns = [('Resign', 'resign'), ('Draw', 'draw'), ('Menu', 'menu'), ('Save', 'save')]
        for i, (label, key) in enumerate(activeBtns):
            bx        = panelX + 5 + i * (btnW + 3)
            rect      = p.Rect(bx, btnY2, btnW, btnH)
            actionRects[key] = rect
            enabled   = key in ('menu', 'save')
            borderCol = p.Color(160, 135, 65) if enabled else p.Color(90, 80, 50)
            textCol   = p.Color(200, 168, 75) if enabled else p.Color(100, 90, 60)
            p.draw.rect(screen, p.Color(65, 65, 65), rect, border_radius=3)
            p.draw.rect(screen, borderCol, rect, width=1, border_radius=3)
            lbl = btnFont.render(label, True, textCol)
            screen.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))

    btnY    = btnY2 - btnH - 6
    btnDefs = [('|<', 'start'), ('<', 'back'), ('>', 'fwd'), ('>|', 'end')]
    navRects = {}
    for i, (label, key) in enumerate(btnDefs):
        bx   = panelX + 5 + i * (btnW + 3)
        rect = p.Rect(bx, btnY, btnW, btnH)
        navRects[key] = rect
        p.draw.rect(screen, p.Color(65, 65, 65), rect, border_radius=3)
        p.draw.rect(screen, p.Color(160, 135, 65), rect, width=1, border_radius=3)
        lbl = btnFont.render(label, True, p.Color(200, 168, 75))
        screen.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.centery - lbl.get_height()//2))

    # clocks above nav buttons
    clockH       = 22
    clockAreaTop = btnY - clockH * 2 - 8

    if whiteTime is not None and blackTime is not None:
        topTime     = blackTime if not flipped else whiteTime
        bottomTime  = whiteTime if not flipped else blackTime
        topLabel    = "BLACK" if not flipped else "WHITE"
        bottomLabel = "WHITE" if not flipped else "BLACK"

        topActive    = (not flipped and not gs.whiteToMove) or (flipped and gs.whiteToMove)
        bottomActive = (not flipped and gs.whiteToMove)     or (flipped and not gs.whiteToMove)
        topColor    = p.Color(200, 168, 75) if topActive    else p.Color(120, 100, 45)
        bottomColor = p.Color(200, 168, 75) if bottomActive else p.Color(120, 100, 45)

        top = fontClock.render(f"{topLabel}  {formatTime(topTime)}", True, topColor)
        bot = fontClock.render(f"{bottomLabel}  {formatTime(bottomTime)}", True, bottomColor)
        screen.blit(top, (panelX + PANEL_WIDTH//2 - top.get_width()//2, clockAreaTop))
        screen.blit(bot, (panelX + PANEL_WIDTH//2 - bot.get_width()//2, clockAreaTop + clockH))

    header = font.render('Move History', True, p.Color(200, 200, 200))
    screen.blit(header, (panelX + PANEL_WIDTH//2 - header.get_width()//2, 6))

    LINE_HEIGHT   = 18
    panelTop      = HEADER_HEIGHT
    panelBottom   = clockAreaTop - 6
    visLines      = (panelBottom - panelTop) // LINE_HEIGHT
    total_lines   = (len(moveHistory) + 1) // 2
    scrollOffset  = max(0, min(scrollOffset, max(0, total_lines - visLines)))

    x_white = panelX + 30
    x_black = panelX + PANEL_WIDTH // 2 + 8

    activeMoveIdx = (viewIndex - 1) if viewIndex is not None else (len(moveHistory) - 1)

    for i in range(visLines):
        lineNr  = scrollOffset + i
        if lineNr >= total_lines:
            break
        moveNr  = lineNr + 1
        moveIdx = lineNr * 2
        y = panelTop + i * LINE_HEIGHT

        nr = font.render(f"{moveNr}.", True, p.Color(150, 150, 150))
        screen.blit(nr, (panelX + 4, y))

        wActive = (moveIdx == activeMoveIdx)
        bActive = (moveIdx + 1 == activeMoveIdx)

        white = font.render(moveHistory[moveIdx], True, p.Color(255, 230, 100) if wActive else p.Color(255, 255, 255))
        screen.blit(white, (x_white, y))

        if moveIdx + 1 < len(moveHistory):
            black = font.render(moveHistory[moveIdx + 1], True, p.Color(255, 230, 100) if bActive else p.Color(200, 200, 200))
            screen.blit(black, (x_black, y))
    # scrollbar
    if total_lines > visLines:
        track_x      = panelX + PANEL_WIDTH - 10
        track_height = panelBottom - panelTop
        p.draw.rect(screen, p.Color(60, 60, 60), p.Rect(track_x, panelTop, 8, track_height))
        thumb_ratio  = visLines / total_lines
        thumb_height = max(20, int(track_height * thumb_ratio))
        thumb_pos    = panelTop + int((scrollOffset / max(1, total_lines)) * track_height)
        p.draw.rect(screen, p.Color(130, 110, 60), p.Rect(track_x, thumb_pos, 8, thumb_height), border_radius=4)

    return navRects, actionRects

def drawCoordinates(screen, flipped=False):
    font = p.font.SysFont('consolas', 10, bold=True)
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
    if flipped:
        files = files[::-1]
        ranks = ranks[::-1]

    for i in range(DIMENSION):
        # color contrast to file color
        on_light = (i % 2 == 0)
        color_on_light = p.Color(100, 90, 70)
        color_on_dark  = p.Color("white")

        # numbers down right, from col = 0 every column
        rank_color = color_on_light if on_light else color_on_dark
        rank_label = font.render(ranks[i], True, rank_color)
        screen.blit(rank_label, (1, i * SQR_SIZE + 1))

        # letters up left, from row = 0 every row
        file_color = color_on_dark if on_light else color_on_light
        file_label = font.render(files[i], True, file_color)
        screen.blit(file_label, (i * SQR_SIZE + SQR_SIZE - 7, HEIGHT - 11))

def savePGN(moveHistory, gameOverResult, settings):
    date = datetime.now().strftime('%Y.%m.%d')
    utcDate = datetime.utcnow().strftime('%Y.%m.%d')
    utcTime = datetime.utcnow().strftime('%H:%M:%S')

    if gameOverResult:
        w = gameOverResult['winner']
        if w == 'White':
            result = '1-0'
        elif w == 'Black':
            result = '0-1'
        else:
            result = '1/2-1/2'
    else:
        result = '*'

    termination = 'Normal'
    if gameOverResult:
        reason = gameOverResult['reason']
        if 'time' in reason:
            termination = 'Time forfeit'
        elif 'resignation' in reason:
            termination = 'Abandoned'

    lines = []
    lines.append(f'[Event "Chess Game"]')
    lines.append(f'[Site "Local"]')
    lines.append(f'[Date "{date}"]')
    lines.append(f'[Round "-"]')
    lines.append(f'[White "White"]')
    lines.append(f'[Black "Black"]')
    lines.append(f'[Result "{result}"]')
    lines.append(f'[UTCDate "{utcDate}"]')
    lines.append(f'[UTCTime "{utcTime}"]')
    lines.append(f'[Variant "Standard"]')
    lines.append(f'[TimeControl "{settings.get("timeLabel", "?")}"]')
    lines.append(f'[Termination "{termination}"]')
    lines.append('')
    lines.append(buildPGN(moveHistory) + ' ' + result)

    filename = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"Saved: {path}")

def drawGameOverPopup(screen, result):
    popupW, popupH = 320, 140
    popupX = (WIDTH - popupW) // 2
    popupY = (HEIGHT - popupH) // 2

    overlay = p.Surface((WIDTH, HEIGHT), p.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    p.draw.rect(screen, p.Color(45, 45, 45), p.Rect(popupX, popupY, popupW, popupH), border_radius=8)
    p.draw.rect(screen, p.Color(200, 168, 75), p.Rect(popupX, popupY, popupW, popupH), width=2, border_radius=8)

    fontTitle  = p.font.SysFont('consolas', 20, bold=True)
    fontSub    = p.font.SysFont('consolas', 14)
    fontClose  = p.font.SysFont('consolas', 13, bold=True)

    winner = result['winner']
    reason = result['reason']

    if winner == 'Draw':
        titleText = 'Draw'
        subText   = reason
    else:
        titleText = f'{winner} wins'
        subText   = reason

    title = fontTitle.render(titleText, True, p.Color(200, 168, 75))
    sub   = fontSub.render(subText,     True, p.Color(200, 200, 200))

    screen.blit(title, (popupX + popupW//2 - title.get_width()//2, popupY + 45))
    screen.blit(sub,   (popupX + popupW//2 - sub.get_width()//2,   popupY + 80))

    # close button
    closeSize = 20
    closeRect = p.Rect(popupX + popupW - closeSize - 8, popupY + 8, closeSize, closeSize)
    p.draw.rect(screen, p.Color(65, 65, 65), closeRect, border_radius=3)
    p.draw.rect(screen, p.Color(160, 135, 65), closeRect, width=1, border_radius=3)
    x_lbl = fontClose.render('x', True, p.Color(200, 168, 75))
    screen.blit(x_lbl, (closeRect.centerx - x_lbl.get_width()//2, closeRect.centery - x_lbl.get_height()//2))

def drawDrawOfferPopup(screen, gs, flipped):
    offering = 'Black' if gs.whiteToMove else 'White'  # prev player offers
    accepting = 'White' if gs.whiteToMove else 'Black'

    popupW, popupH = 280, 110
    popupX = (WIDTH - popupW) // 2
    # popup for accepting player
    if (accepting == 'White' and not flipped) or (accepting == 'Black' and flipped):
        popupY = HEIGHT - popupH - 20  
    else:
        popupY = 20

    overlay = p.Surface((WIDTH, HEIGHT), p.SRCALPHA)
    overlay.fill((0, 0, 0, 80))
    screen.blit(overlay, (0, 0))

    p.draw.rect(screen, p.Color(45, 45, 45), p.Rect(popupX, popupY, popupW, popupH), border_radius=8)
    p.draw.rect(screen, p.Color(200, 168, 75), p.Rect(popupX, popupY, popupW, popupH), width=2, border_radius=8)

    fontSub  = p.font.SysFont('consolas', 12)
    fontBtn  = p.font.SysFont('consolas', 11, bold=True)

    txt = fontSub.render(f'{offering} offers a draw', True, p.Color(200, 200, 200))
    screen.blit(txt, (popupX + popupW//2 - txt.get_width()//2, popupY + 14))

    btnW, btnH = 90, 26
    acceptRect = p.Rect(popupX + popupW//2 - btnW - 8, popupY + popupH - btnH - 12, btnW, btnH)
    declineRect = p.Rect(popupX + popupW//2 + 8,        popupY + popupH - btnH - 12, btnW, btnH)

    p.draw.rect(screen, p.Color(65, 65, 65), acceptRect,  border_radius=3)
    p.draw.rect(screen, p.Color(160, 135, 65), acceptRect, width=1, border_radius=3)
    p.draw.rect(screen, p.Color(65, 65, 65), declineRect, border_radius=3)
    p.draw.rect(screen, p.Color(160, 135, 65), declineRect, width=1, border_radius=3)

    a = fontBtn.render('Accept', True, p.Color(200, 168, 75))
    d = fontBtn.render('Decline', True, p.Color(200, 168, 75))
    screen.blit(a, (acceptRect.centerx  - a.get_width()//2, acceptRect.centery  - a.get_height()//2))
    screen.blit(d, (declineRect.centerx - d.get_width()//2, declineRect.centery - d.get_height()//2))

    return acceptRect, declineRect, popupY

if __name__ == "__main__":
    main()
