import math
import pygame as p
import ChessEngine
import Minmax


WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 290
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 240
IMAGES = {}

def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False
    playerOne = True   
    playerTwo = False
    load_images()
    sqSelected = ()
    playerClicks = []
    flipBoard = False  # Default: White at bottom


    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE

                    if flipBoard:  # Adjust row and column for flipped board
                        row = DIMENSION - 1 - row
                        col = DIMENSION - 1 - col
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        if move in validMoves:
                            move = validMoves[validMoves.index(move)]
                            gs.makeMove(move)
                            moveMade = True
                            animate = True
                            sqSelected = ()
                            playerClicks = []
                            print(move.getChessNotation())
                        else:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    playerOne = True
                    playerTwo = True
                elif e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    moveMade = False
                    animate = False
                    gameOver = False
                    playerOne = True
                    playerTwo = True
                    sqSelected = ()
                    playerClicks = []
                elif e.key == p.K_q:  # Play as Black
                    playerOne = False
                    playerTwo = True
                    flipBoard = True  # Rotate board so Black is at bottom
                elif e.key == p.K_e:  # Play as White
                    playerOne = True
                    playerTwo = False
                    flipBoard = False  # Keep White at bottom


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, flipBoard)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        ''' AI move finder '''
        if not gameOver and not humanTurn:
            AIMove = Minmax.findBestMoveMinimax(gs, validMoves)
            #AIMove = ChienKoNgu.findRandomMove(validMoves)
            if AIMove is None:   #when begin the game
                AIMove = Minmax.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
            print(AIMove.getChessNotation())


        drawGameState(screen, gs, validMoves, sqSelected, flipBoard)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            if gs.staleMate:
                gameOver = True
                drawEndGameText(screen, "DRAW")
            else:
                if gs.whiteToMove:
                    drawEndGameText(screen, "BLACK WIN")
                else:
                    drawEndGameText(screen, "WHITE WIN")


        clock.tick(MAX_FPS)
        p.display.flip()

def highlightMove(screen, gs, validMoves, sqSelected, flipBoard):
    sq = p.Surface((SQ_SIZE, SQ_SIZE))
    sq.set_alpha(100)

    def flipCoords(r, c):
        """If flipBoard is True, flip the row and column to adjust for perspective."""
        return (7 - r, 7 - c) if flipBoard else (r, c)

    if sqSelected != ():
        r, c = flipCoords(*sqSelected)  # Adjust for flipping
        if gs.board[sqSelected[0]][sqSelected[1]][0] == ('w' if gs.whiteToMove else 'b'):  # Valid piece selection
            # Highlight selected square
            sq.fill(p.Color("blue"))
            screen.blit(sq, (c * SQ_SIZE, r * SQ_SIZE))

            # Highlight valid moves
            sq.fill(p.Color("cyan"))
            for move in validMoves:
                if move.startRow == sqSelected[0] and move.startCol == sqSelected[1]:
                    endR, endC = flipCoords(move.endRow, move.endCol)  # Flip move destinations
                    screen.blit(sq, (endC * SQ_SIZE, endR * SQ_SIZE))

    # Highlight king in check
    if gs.inCheck:
        kingR, kingC = flipCoords(*gs.whiteKingLocate if gs.whiteToMove else gs.blackKingLocate)
        sq.fill(p.Color("red"))
        screen.blit(sq, (kingC * SQ_SIZE, kingR * SQ_SIZE))

    # Highlight last move
    if len(gs.moveLog) != 0:
        startR, startC = flipCoords(gs.moveLog[-1].startRow, gs.moveLog[-1].startCol)
        endR, endC = flipCoords(gs.moveLog[-1].endRow, gs.moveLog[-1].endCol)
        sq.fill(p.Color("yellow"))
        screen.blit(sq, (startC * SQ_SIZE, startR * SQ_SIZE))
        screen.blit(sq, (endC * SQ_SIZE, endR * SQ_SIZE))



def animateMove(move, screen, board, clock, flipBoard):
    colors = [p.Color("white"), p.Color("grey")]

    # Original start and end positions
    startR, startC = move.startRow, move.startCol
    endR, endC = move.endRow, move.endCol

    # Calculate movement direction before flipping
    dR, dC = endR - startR, endC - startC  

    # Flip coordinates if playing as Black
    if flipBoard:
        startR, startC = 7 - move.startRow, 7 - move.startCol
        endR, endC = 7 - move.endRow, 7 - move.endCol
        dR, dC = endR - startR, endC - startC  # Recalculate movement direction

    # Compute movement distance
    sqDistance = math.sqrt(dR ** 2 + dC ** 2)
    sqDistance = max(1, int(sqDistance))  # Avoid division by zero

    framesPerSquare = 12 // sqDistance
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare  

    for frame in range(frameCount + 1):
        # Smooth interpolation
        r = startR + (dR * frame / frameCount)
        c = startC + (dC * frame / frameCount)

        drawBoard(screen, flipBoard)
        drawPieces(screen, board, flipBoard)

        # Highlight destination square
        color = colors[(endR + endC) % 2]
        endSquare = p.Rect(endC * SQ_SIZE, endR * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # Handle captured pieces (including En Passant)
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = move.endRow - 1 if move.pieceCaptured[0] == 'b' else move.endRow + 1
                if flipBoard:
                    enPassantRow = 7 - enPassantRow
                endSquare = p.Rect(endC * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # Draw the moving piece at its interpolated position
        if move.pieceMoved != "--":
            pieceRect = p.Rect(int(c) * SQ_SIZE, int(r) * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceMoved], pieceRect)

        p.display.flip()
        clock.tick(144)



def drawGameState(screen, gs, validMoves, sqSelected, flipBoard):
    drawBoard(screen, flipBoard)
    highlightMove(screen, gs, validMoves, sqSelected, flipBoard)
    drawPieces(screen, gs.board, flipBoard)
    drawMoveLog(screen, gs)

def drawBoard(screen, flipBoard):
    colors = [p.Color("white"), p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            row = r if not flipBoard else DIMENSION - 1 - r  # Flip rows if needed
            col = c if not flipBoard else DIMENSION - 1 - c  # Flip columns if needed
            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board, flipBoard):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            row = r if not flipBoard else DIMENSION - 1 - r  # Flip row
            col = c if not flipBoard else DIMENSION - 1 - c  # Flip column
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawEndGameText(screen, text):
    font = p.font.SysFont("Verdana", 32, True, False)
    textObject = font.render(text, False, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("red"))
    screen.blit(textObject, textLocation.move(2, 2))

def drawMoveLog(screen, gs):
    moveLogRect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "   "
        moveTexts.append(moveString)
    
    padding = 5
    movesPerRow = 3
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        font = p.font.SysFont("Verdana", 13, True, False)
        for j in range(movesPerRow):
            if i+j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, False, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


if __name__ == "__main__":
    main()