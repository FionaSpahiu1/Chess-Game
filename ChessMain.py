# Handles user input and displays current state information
# import gs as gs
import pygame
import pygame as p
import ChessEngine
pygame.init()
pygame.display.set_caption('CHESS GAME')
import chessAI

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animation later on
IMAGES = {}

# loading the images: save them only once and re-use them as variables
def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("ChessPieces/" + piece + ".png"), (40, 50))

    # NOTE: p.transform.scale - images to match the squares
    # NOTE: we can access the image by typing IMAGES["wB"]


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))  # add commands here for later
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()  # creates  gs(GameState object, calling our instructions
    legalMoves = gs.getValidMoves()
    moveMade = False

    load_images()  # only this once,before the while loop
    running = True
    sqSelected = ()  # keep track of the last click of the user tuple(rank /row,file / col)
    playerClicks = []  # keep track of player clicks // two tuples
    playerWhite = True  # If human is playing white - true and if AI playing white - false
    playerBlack = False  # If human playing black - False and if AI playing black - False
    while running:
        humanMove = (gs.whiteToMove and playerWhite) or (not gs.whiteToMove and playerBlack)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if humanMove:
                    location = p.mouse.get_pos()  # x,y location of mouse
                    Col = location[0]//SQ_SIZE  # rank
                    Row = location[1]//SQ_SIZE  # file
                    if sqSelected == (Row, Col):  # user clicks the same square twice
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear user click
                    else:
                        sqSelected = (Row, Col)
                        playerClicks.append(sqSelected)  # append for both clicks
                    if len(playerClicks) == 2:  # after the 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1],gs.board)
                        piece1 = gs.returnPiece(playerClicks[0])
                        piece2 = gs.returnPiece(playerClicks[1])
                        if piece1[1] == "K" and piece2[1] == "R" or piece1[1] == "R" and piece2[1] == "K":
                            move.Castle = True
                        for i in range(len(legalMoves)):
                            if move.Castle:
                                if legalMoves[i].Castle:
                                    gs.makeMove(legalMoves[i])
                                    moveMade = True
                                    sqSelected = ()
                                    playerClicks = []
                            elif move == legalMoves[i]:
                                gs.makeMove(legalMoves[i])
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # Key Handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_a:  # press z to undo move
                    gs.undoMove()
                    moveMade = True
                if e.key == p.K_z: # Reset the game
                    gs = ChessEngine.GameState()
                    legalMoves = gs.legalMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
        # AI find Random Moves
        if not humanMove:
            AI = chessAI.bestMove(gs,legalMoves)
            gs.makeMove(AI)
            moveMade = True
        if moveMade:
            legalMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs,legalMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

# Responsible for the graphics within the current game state

def drawGameState(screen, gs, legalMoves, sqSelected):
    drawBoard(screen)  # draw squares on the board
    highlights(screen, gs, legalMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on these squares

# the top left square is always light
def highlights(screen, gs, legalMoves,sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"): # selected piece can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE)) #highlight the selected square
            s.set_alpha(70) #Transparency level: 0 - empty to 255 - obaque
            s.fill(p.Color("Pink"))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(p.Color("Blue"))
            for move in legalMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))




def drawBoard(screen):
    colors = [p.Color("white"), p.Color(82, 82, 82)]
    for r in range(DIMENSION):  # r - row c - column
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE,r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE + SQ_SIZE / 5, r * SQ_SIZE + SQ_SIZE / 5,
                                                  SQ_SIZE,SQ_SIZE))

# Highlight possible squares for piece selected

if __name__ == "__main__":
    main()
