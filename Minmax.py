import random
import time


pieceScore = {"K": 0, "Q": 90, "R": 50, "B": 35, "N": 30, "p": 10}

knightScore =  [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScore =  [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScore =   [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rookScore =    [[4, 3, 4, 4, 4, 4, 3, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScore =   [[8, 8, 8, 8, 8, 8, 8, 8],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScore =   [[0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [1, 2, 3, 3, 3, 3, 2, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [8, 8, 8, 8, 8, 8, 8, 8]]

piecePosScores =  {'N': knightScore, 'B': bishopScore, 'Q': queenScore, 'R': rookScore, "wp": whitePawnScore, "bp": blackPawnScore}


CHECKMATE = 100000
STALEMATE = 0
MAX_DEPTH = 4

''' Find random move for AI '''
def findRandomMove(validMoves):
    if len(validMoves) > 0:
        return validMoves[random.randint(0, len(validMoves)-1)]


import time

import time

def findBestMoveMinimax(gs, validMoves, difficulty="Medium"):  
    global nextMove, nodes
    nextMove = None
    alpha = -CHECKMATE
    beta = CHECKMATE
    nodes = 0
    start_time = time.time()  

    # Map difficulty to search depth
    depth_map = {"Easy": 2, "Medium": 3, "Hard": 4}
    search_depth = depth_map.get(difficulty, 4)  # Default to Medium

    bestMove = None
    bestScore = -CHECKMATE

    for move in validMoves:
        gs.makeMove(move)
        score = findMoveMinimax(gs, validMoves, search_depth - 1, alpha, beta, not gs.whiteToMove, start_time, search_depth)  # ✅ Passed validMoves
        gs.undoMove()

        if score > bestScore:
            bestScore = score
            bestMove = move

        # **Check Time Cap (30s)**
        if time.time() - start_time > 30:
            print("Time limit reached, returning best move found so far.")
            return bestMove if bestMove else findRandomMove(validMoves)

    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time:.2f} sec")
    print(f"Nodes searched: {nodes}")

    return bestMove if bestMove else findRandomMove(validMoves)




def findMoveMinimax(gs, validMoves, depth, alpha, beta, whiteToMove, start_time, search_depth):
    """Minimax function with alpha-beta pruning and timeout handling."""
    global nextMove, nodes
    nodes += 1

    # Check if computation time exceeds 30 seconds
    if time.time() - start_time > 30:
        return scoreBoard(gs)  # Return best score found before timeout

    if depth == 0 or gs.checkMate or gs.staleMate:
        return scoreBoard(gs)

    bestMove = None
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinimax(gs, nextMoves, depth - 1, alpha, beta, False, start_time, search_depth)  # ✅ Pass search_depth
            gs.undoMove()

            if score > maxScore:
                maxScore = score
                bestMove = move
                if depth == search_depth:  # ✅ Use search_depth instead of undefined MAX_DEPTH
                    nextMove = move  # Save best move found

            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return maxScore

    else:  # Black to move
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinimax(gs, nextMoves, depth - 1, alpha, beta, True, start_time, search_depth)  # ✅ Pass search_depth
            gs.undoMove()

            if score < minScore:
                minScore = score
                bestMove = move
                if depth == search_depth:  # ✅ Use search_depth instead of MAX_DEPTH
                    nextMove = move  # Save best move found

            beta = min(beta, score)
            if beta <= alpha:
                break
        return minScore



def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  #black win
        else:
            return CHECKMATE   #white win
    elif gs.staleMate:
        return STALEMATE
    # if not checkmate or stalemate:
    score = 0
    for row in range(8):
        for col in range(8):
            square = gs.board[row][col]
            if square != "--":
                piecePosScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piecePosScore = piecePosScores[square][row][col]
                    else:
                        piecePosScore = piecePosScores[square[1]][row][col]
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePosScore
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePosScore
    return score


