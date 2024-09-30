import random

points = { "K": 0, "Q": 9, "R": 5,"B": 3, "N":3, "p":1}
CHECKMATE = 1000
STALEMATE = 1
def randomAI(legalMoves):
    return legalMoves[random.randint(0,len(legalMoves)-1)]


# Best moves based on materials(only)
def bestMove(gs, legalMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1  # keep track on whose turn is it
    opponentminmaxScore = CHECKMATE  # minimum opportunity for max score for opponent = best move for us
    bestMove = None
    for playerMove in legalMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.legalMoves()
        opponentmaxScore = -CHECKMATE
        for opponentMove in opponentMoves:
            gs.makeMove(opponentMove)
            if gs.CheckMate:
                score = -turnMultiplier * CHECKMATE
            else:
                score = -turnMultiplier * scoreM(gs.board)
            if score > opponentmaxScore:
                opponentmaxScore = score
            gs.undoMove()
        if opponentminmaxScore > opponentmaxScore:
            opponentminmaxScore = opponentmaxScore
            bestMove = playerMove
        gs.undoMove()
    return bestMove

def scoreM(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += points[square[1]]
            if square[0] == "b":
                score -= points[square[1]]
    return score


# Score the board bared on material
