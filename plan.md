# Chess development plan

1. In engine class GameState() def __init__(self)

2. Use numpy array two dimensional, for the board 8x8 self.board
["bR", "bN", ...],
["bP", "bP", ...],
["--", "--", ...]

3. Initialize  
- `self.whiteToMove = True`  
- `self.moveLog = []`

4. In `main.py`  
- Import pygame and engine  
- Initialize pygame: `p.init()` (doesn't matter that much)  
- Set up screen:  
```python
width = height = 512 #(or diff 400)
dimensions = 8
squareSize = height // dimension
fps = 15 , for animations tbd
images = {}
```

5. Load images once, create a dictionary of images, call it once in main:
```python
def loadImages():
    IMAGES['wP'] = p.image.load("img/wP.png"), but it's too much code
    pieces = ['wP', 'wR', ...]
    for piece in pieces: 
        IMAGES[pieces] = p.image.load("img/" + piece + ".png")
```
Access the images by IMAGES['wP']

We want to scale the images of pieces
IMAGES[pieces] = p.transform.scale(p.image.load("img/" + piece + ".png"), (squareSize, squareSize))

6. User input and updating graphics in main.py
```python
def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    #print(gs.board)
    loadImages() # call once
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
            running = False
        clock.tick(fps)
        p.display.flip()

this at the end of code
if __name__ == "__main__":
    main()
```

7. Drawing the game state in the while running loop

```python
def drawGameState(screen, gs):
    drawBoard(screen) # draw squares on board
    #add highlights or move suggestions tbd
    drawPieces(screen, gs.board) draw pieces on top of squares

def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range (dimension):
        for c in range (dimension):
            color = colors[((r+c)%2)] 
            p.draw.rect(screen, color, p.Rect(c*squareSize, r*squareSize, squareSize,squareSize))
def drawPieces(screen, board): # iterate through rows and columns,
# using board from engine.py check if a piece is not '--' and draw the piece
```

TBD 
8. User input, clicks and selections
add mouse event handling in main.py in while running: loop,
track two clicks first for the piece, second for destination
call gs.makeMove(move) when a valid move is detected

9. Create a Move Class in engine.py that stores
start square (row, col),
end square,
piece moved/captured.
(?) add a __str__() method to display moves like e2e4

10. Move execution in engine.py
Add a method makeMove(move) that
modifies the 'board',
appends the move to moveLog,
flips whiteToMove
(?) undoMove() for taking back a move

11. Generate valid moves in engine.py
Add getValidMoves() and getAllPossibleMoves()
(basic movement for each piece for now)

12. Check input validity in main.py
use the list from gs.getValidMoves()
only allow makeMove() if move is in valid list

13. Drawing highlights in main.py
update drawGameState() to include
currently selected square,
valid moves for selected piece.
(?) highlight last move

14. Undo function in main.py+engine.py
add a key event (like a z key)
call gs.undoMove() - method in engine.py
