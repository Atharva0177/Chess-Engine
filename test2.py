import math
import pygame as p
import ChessEngine
import Minmax
import concurrent.futures
import time


WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 290
DIFFICULTY_PANEL_WIDTH = 150  # New panel width
TOTAL_WIDTH = WIDTH + MOVE_LOG_PANEL_WIDTH + DIFFICULTY_PANEL_WIDTH
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 240
IMAGES = {}

def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def drawTimer(screen, start_time):
    """Displays the AI's thinking time on the screen."""
    elapsed_time = time.time() - start_time
    font = p.font.SysFont("Arial", 20, True, False)
    text_surface = font.render(f"AI Thinking: {elapsed_time:.1f} sec", True, p.Color("black"))
    screen.blit(text_surface, (WIDTH + 10, HEIGHT - 40))  # Position at bottom right

WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 290
DIFFICULTY_PANEL_WIDTH = 150  # New panel width
TOTAL_WIDTH = WIDTH + MOVE_LOG_PANEL_WIDTH + DIFFICULTY_PANEL_WIDTH
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 240
IMAGES = {}

def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def drawTimer(screen, start_time):
    """Displays the AI's thinking time on the screen."""
    elapsed_time = time.time() - start_time
    font = p.font.SysFont("Arial", 20, True, False)
    text_surface = font.render(f"AI Thinking: {elapsed_time:.1f} sec", True, p.Color("black"))
    screen.blit(text_surface, (WIDTH + 10, HEIGHT - 40))

def main():
    p.init()
    screen = p.display.set_mode((TOTAL_WIDTH, HEIGHT))
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
    flipBoard = False
    difficulty = "Medium"  # Default difficulty
    ai_thinking_time = 0  # **AI Timer Variable**

    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                x, y = p.mouse.get_pos()
                if x >= WIDTH + MOVE_LOG_PANEL_WIDTH:  # Click inside difficulty panel
                    difficulty = select_difficulty(y)
                elif not gameOver and humanTurn:
                    col, row = x // SQ_SIZE, y // SQ_SIZE
                    if flipBoard:
                        row, col = DIMENSION - 1 - row, DIMENSION - 1 - col
                    if sqSelected == (row, col) or col >= 8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade, animate = True, True
                            sqSelected, playerClicks = (), []
                        else:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_s:  # Switch sides (flip the board)
                    flipBoard = not flipBoard
                    playerOne, playerTwo = playerTwo, playerOne
                
                elif e.key == p.K_z:  # Undo the last move
                    if len(gs.moveLog) > 0:
                        gs.undoMove()
                        moveMade = True
                        animate = False
                        gameOver = False  # Reset game over status
                
                elif e.key == p.K_r:  # Reset the board
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    ai_thinking_time = 0  # **Reset AI Timer**

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, flipBoard)
            validMoves = gs.getValidMoves()
            moveMade, animate = False, False

        if not gameOver and not humanTurn:
            AIMove = None
            start_time = time.time()  # **Track AI Start Time**
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(Minmax.findBestMoveMinimax, gs, validMoves, difficulty)
                try:
                    AIMove = future.result(timeout=30)  # Time cap of 30 seconds
                except concurrent.futures.TimeoutError:
                    print("AI move timed out! Playing a random move.")
                    if validMoves:
                        AIMove = validMoves[0]  # Fallback: Choose the first valid move
            
            ai_thinking_time = time.time() - start_time  # **Calculate AI Thinking Time**
            
            if AIMove:
                gs.makeMove(AIMove)
                moveMade, animate = True, True

        drawGameState(screen, gs, validMoves, sqSelected, flipBoard, ai_thinking_time)  # **Pass AI Timer**
        drawDifficultyPanel(screen, difficulty)

        if gs.checkMate or gs.staleMate:
            gameOver = True
            drawEndGameText(screen, "DRAW" if gs.staleMate else "BLACK WIN" if gs.whiteToMove else "WHITE WIN")

        clock.tick(MAX_FPS)
        p.display.flip()

def select_difficulty(y):
    if y < HEIGHT // 3:
        return "Easy"
    elif y < 2 * HEIGHT // 3:
        return "Medium"
    return "Hard"

def drawDifficultyPanel(screen, difficulty):
    panelRect = p.Rect(WIDTH + MOVE_LOG_PANEL_WIDTH, 0, DIFFICULTY_PANEL_WIDTH, HEIGHT)
    p.draw.rect(screen, p.Color("darkgrey"), panelRect)
    font = p.font.SysFont("Verdana", 20, True)
    for i, level in enumerate(["Easy", "Medium", "Hard"]):
        color = p.Color("yellow") if level == difficulty else p.Color("black")
        text = font.render(level, True, color)
        screen.blit(text, (WIDTH + MOVE_LOG_PANEL_WIDTH + 20, i * HEIGHT // 3 + 50))



def drawEndGameText(screen, text):
    font = p.font.SysFont("Verdana", 32, True, False)
    textObject = font.render(text, False, p.Color("black"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("red"))
    screen.blit(textObject, textLocation.move(2, 2))

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



def drawGameState(screen, gs, validMoves, sqSelected, flipBoard, ai_thinking_time):
    drawBoard(screen, flipBoard)
    highlightMove(screen, gs, validMoves, sqSelected, flipBoard)
    drawPieces(screen, gs.board, flipBoard)
    drawMoveLog(screen, gs)
    
    # **Draw AI Thinking Time**
    font = p.font.Font(None, 36)
    text = font.render(f"AI Time: {ai_thinking_time:.2f}s", True, p.Color("black"))
    
    # **Position the Timer on the Right Panel**
    screen.blit(text, (WIDTH + 20, HEIGHT - 50))  

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


# def drawEndGameText(screen, text):
#     font = p.font.SysFont("Verdana", 32, True, False)
#     textObject = font.render(text, False, p.Color("black"))
#     textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
#     screen.blit(textObject, textLocation)
#     textObject = font.render(text, False, p.Color("red"))
#     screen.blit(textObject, textLocation.move(2, 2))

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