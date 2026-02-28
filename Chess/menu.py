import pygame as p
import sys

p.init()

WIDTH = 732
HEIGHT = 512
screen = p.display.set_mode((WIDTH, HEIGHT))
p.display.set_caption("Chess")

BG          = p.Color(67, 67, 67)
BTN_NORMAL  = p.Color(67, 67, 67)
BTN_HOVER   = p.Color(95, 95, 95)
BTN_SEL     = p.Color(105, 105, 105)
BORDER      = p.Color(90, 90, 90)
BORDER_SEL  = p.Color(200, 168, 75)
GOLD        = p.Color(200, 168, 75)
GOLD_DIM    = p.Color(160, 135, 65)
TEXT        = p.Color(220, 210, 185)
TEXT_DIM    = p.Color(140, 130, 110)
TEXT_SEL    = p.Color(220, 200, 140)

FONT_TITLE  = p.font.SysFont('consolas', 36, bold=True)
FONT_LARGE  = p.font.SysFont('consolas', 13, bold=True)
FONT_MEDIUM = p.font.SysFont('consolas', 12)
FONT_SMALL  = p.font.SysFont('consolas', 10)

TIME_CONTROLS = [
    ("1+0",    60,   0, "Bullet"),
    ("1+1",    60,   1, "Bullet"),
    ("3+0",   180,   0, "Blitz"),
    ("3+2",   180,   2, "Blitz"),
    ("5+0",   300,   0, "Blitz"),
    ("10+0",  600,   0, "Rapid"),
    ("15+10", 900,  10, "Rapid"),
    ("30+0", 1800,   0, "Classical"),
]

class MenuState:
    def __init__(self):
        self.selectedMode  = None
        self.selectedTime  = 5
        self.selectedColor = 'random'
        self.hovered       = None

def drawBtn(surface, rect, selected, hovered):
    color  = BTN_SEL    if selected else (BTN_HOVER if hovered else BTN_NORMAL)
    border = BORDER_SEL if selected else (BTN_HOVER if hovered else BORDER)
    p.draw.rect(surface, color,  rect, border_radius=3)
    p.draw.rect(surface, border, rect, width=2, border_radius=3)

def drawSection(surface, text, y):
    lbl = FONT_SMALL.render(text, True, GOLD_DIM)
    surface.blit(lbl, (32, y))
    lineX = 32 + lbl.get_width() + 8
    p.draw.line(surface, GOLD_DIM, (lineX, y + 5), (WIDTH - 32, y + 5), 1)

def drawMenu(state):
    screen.fill(BG)

    shadow = FONT_TITLE.render("CHESS", True, p.Color(40, 30, 5))
    title  = FONT_TITLE.render("CHESS", True, GOLD)
    tx = WIDTH // 2 - title.get_width() // 2
    screen.blit(shadow, (tx + 3, 28))
    screen.blit(title,  (tx, 25))
    p.draw.line(screen, GOLD_DIM, (32, 72), (WIDTH - 32, 72), 1)

    y = 88

    # GAME MODE
    drawSection(screen, "GAME MODE", y)
    y += 20

    modes = [
        ('local',  '1v1  Local', TEXT),
        ('easy',   'Easy Bot',   TEXT),
        ('medium', 'Medium Bot', TEXT),
        ('hard',   'Hard Bot',   TEXT),
    ]

    bw = (WIDTH - 72 - 10) // 2
    bh = 42
    modeRects = {}

    for i, (key, label, color) in enumerate(modes):
        col  = i % 2
        row  = i // 2
        bx   = 32 + col * (bw + 10)
        by   = y + row * (bh + 8)
        rect = p.Rect(bx, by, bw, bh)
        modeRects[key] = rect
        sel  = state.selectedMode == key
        hov  = state.hovered == ('mode', key)
        drawBtn(screen, rect, sel, hov)
        lbl  = FONT_MEDIUM.render(label, True, TEXT_SEL if sel else color)
        screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                          rect.centery - lbl.get_height() // 2))

    y += 2 * (bh + 8) + 18

    # TIME CONTROL
    drawSection(screen, "TIME CONTROL", y)
    y += 20

    cols      = 4
    bwT       = (WIDTH - 72 - (cols - 1) * 8) // cols
    bhT       = 40
    timeRects = {}

    for i, (label, base, inc, cat) in enumerate(TIME_CONTROLS):
        col  = i % cols
        row  = i // cols
        bx   = 32 + col * (bwT + 8)
        by   = y + row * (bhT + 8)
        rect = p.Rect(bx, by, bwT, bhT)
        timeRects[i] = rect
        sel  = state.selectedTime == i
        hov  = state.hovered == ('time', i)
        drawBtn(screen, rect, sel, hov)
        tl   = FONT_LARGE.render(label, True, TEXT_SEL if sel else TEXT)
        cl   = FONT_SMALL.render(cat,   True, TEXT_SEL  if sel else TEXT_DIM)
        screen.blit(tl, (rect.centerx - tl.get_width() // 2, rect.y + 6))
        screen.blit(cl, (rect.centerx - cl.get_width() // 2, rect.y + 23))

    rowsT = (len(TIME_CONTROLS) + cols - 1) // cols
    y += rowsT * (bhT + 8) + 18

    # PLAY AS
    drawSection(screen, "PLAY AS", y)
    y += 20

    colorOpts  = [('white', 'White'), ('random', 'Random'), ('black', 'Black')]
    bwC        = (WIDTH - 72 - 2 * 10) // 3
    bhC        = 46
    colorRects = {}

    for i, (key, label) in enumerate(colorOpts):
        bx   = 32 + i * (bwC + 10)
        rect = p.Rect(bx, y, bwC, bhC)
        colorRects[key] = rect
        sel  = state.selectedColor == key
        hov  = state.hovered == ('color', key)
        drawBtn(screen, rect, sel, hov)

        sw = 18
        sx = rect.centerx - sw // 2
        sy = rect.y + 7
        if key == 'white':
            p.draw.rect(screen, p.Color(232, 217, 176), p.Rect(sx, sy, sw, sw), border_radius=2)
        elif key == 'black':
            p.draw.rect(screen, p.Color(42, 42, 62),   p.Rect(sx, sy, sw, sw), border_radius=2)
            p.draw.rect(screen, p.Color(80, 80, 100),  p.Rect(sx, sy, sw, sw), width=1, border_radius=2)
        else:
            p.draw.rect(screen, p.Color(232, 217, 176), p.Rect(sx,           sy, sw // 2, sw), border_radius=2)
            p.draw.rect(screen, p.Color(42,  42,  62),  p.Rect(sx + sw // 2, sy, sw // 2, sw), border_radius=2)

        lbl = FONT_SMALL.render(label, True, TEXT_SEL if sel else TEXT)
        screen.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.y + 30))

    y += bhC + 24

    # START
    startRect = p.Rect(32, y, WIDTH - 64, 50)
    canStart  = state.selectedMode is not None
    sc = BTN_SEL if canStart else p.Color(55, 55, 55)
    sb = BORDER_SEL if canStart else BORDER
    if state.hovered == ('start',) and canStart:
        sc = BTN_HOVER
    stc = TEXT_DIM if not canStart else TEXT
    p.draw.rect(screen, sc, startRect, border_radius=3)
    p.draw.rect(screen, sb, startRect, width=2, border_radius=3)

    st  = "SELECT A MODE TO START" if not canStart else "START GAME"
    lbl = FONT_LARGE.render(st, True, stc)
    screen.blit(lbl, (startRect.centerx - lbl.get_width() // 2,
                      startRect.centery - lbl.get_height() // 2))

    p.display.flip()
    return startRect, modeRects, timeRects, colorRects


def getHover(mx, my, modeRects, timeRects, colorRects, startRect):
    for key, rect in modeRects.items():
        if rect.collidepoint(mx, my):
            return ('mode', key)
    for i, rect in timeRects.items():
        if rect.collidepoint(mx, my):
            return ('time', i)
    for key, rect in colorRects.items():
        if rect.collidepoint(mx, my):
            return ('color', key)
    if startRect and startRect.collidepoint(mx, my):
        return ('start',)
    return None

def main():
    state      = MenuState()
    clock      = p.time.Clock()
    startRect  = None
    modeRects  = {}
    timeRects  = {}
    colorRects = {}

    while True:
        mx, my = p.mouse.get_pos()
        state.hovered = getHover(mx, my, modeRects, timeRects, colorRects, startRect)
        startRect, modeRects, timeRects, colorRects = drawMenu(state)

        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN and e.button == 1:
                h = getHover(mx, my, modeRects, timeRects, colorRects, startRect)
                if h is None:
                    continue
                if h[0] == 'mode':
                    state.selectedMode = h[1]
                elif h[0] == 'time':
                    state.selectedTime = h[1]
                elif h[0] == 'color':
                    state.selectedColor = h[1]
                elif h[0] == 'start' and state.selectedMode:
                    td = TIME_CONTROLS[state.selectedTime]
                    return {
                        'mode':      state.selectedMode,
                        'timeLabel': td[0],
                        'baseTime':  td[1],
                        'increment': td[2],
                        'color':     state.selectedColor,
                    }

        clock.tick(60)

if __name__ == '__main__':
    result = main()
    print(result)