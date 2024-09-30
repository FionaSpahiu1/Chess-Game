# This is where we store the information for the current state + determining the legal moves at current state

from pygame.color import Color
class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.MoveFunctions = {"p": self.PawnMoves, "R": self.RookMoves, "N": self.KnightMoves,
                              "B": self.BishopMoves, "Q": self.QueenMoves, "K": self.KingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCHECK = False
        self.Pins = []
        self.Checks = []
        self.CheckMate = False
        self.StaleMate = False
        self.enPassantPossible = ()  # coordinates for possible enPassant moves
        # Current Castling Rights
        self.CastlingNow = CastleRights(True, True,True,True)
        self.CastleRightsLog = [CastleRights(self.CastlingNow.wqs, self.CastlingNow.bqs,
                                                     self.CastlingNow.wks, self.CastlingNow.bks)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move to undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
        # Update King's location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        #  Pawn Promotion
        if move.PawnPromotion: # promotion to Q, R ,B , N
            promotedPiece = input("Promote to Q, R, B or N ?")
            if promotedPiece == "Q":
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
            elif promotedPiece == "R":
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "R"
            elif promotedPiece == "B":
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "B"
            else:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "N"
        #En Passant
        if move.enPassantmove:
            self.board[move.startRow][move.endCol] = "--"  # capture the pawn
        #Update the enPassantPossible Variable
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) //2, move.startCol)
        else:
            self.enPassantPossible = ()
        # Castling Rights need to be updated whenever a rook or the king moves
        # Castle Moves
        if move.Castle:
            if move.endCol - move.startCol == 2: # Kingside
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] # Move rook
                self.board[move.endRow][move.endCol + 1] = "--"
            else:  # Queenside
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # Move Rook
                self.board[move.endRow][move.endCol - 2] = "--"
            self.CastlingRights(move)
            self.CastleRightsLog.append(CastleRights(self.CastlingNow.wqs, self.CastlingNow.bqs,
                                                 self.CastlingNow.wks, self.CastlingNow.bks))

    def undoMove(self):  # undo last move
        if len(self.moveLog) != 0:  # there should be a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Update King's location if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            #  Undo EnPassant
            if move.enPassantmove:
                self.board[move.endRow][move.endCol] = "--" # leave the landing square of the pawn empty
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)
            #  Undo a 2 square pawn advance
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

            # Undo Castle Move
            if move.Castle:
                if move.endCol - move.startCol == 2: #  Kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]  # move rook
                    self.board[move.endRow][move.endCol - 1] = "--"  # empty space where rook was
                else: #  Queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1] # Move rook
                    self.board[move.endRow][move.endCol + 1] = "--"  # empty space where rook was

    # All moves considering checks
    def legalMoves(self):
        for log in self.CastleRightsLog:
            print(log.wks,log.bks,log.wqs,log.bqs, end=", ")
        print()
        moves = []
        # Creating Castle moves + adding it to the (moves = []) array
        if self.whiteToMove:
            self.CastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1],moves, "w")
        else:
            self.CastleMoves(self.blackKingLocation[0],self.blackKingLocation[1], moves, "b")
        self.inCHECK, self.Pins, self.Checks = self.FindPinsandChecks()
        if self.whiteToMove:  # defining the location of each king
            KingRow = self.whiteKingLocation[0]
            KingCol = self.whiteKingLocation[1]
        else:
            KingRow = self.blackKingLocation[0]
            KingCol = self.blackKingLocation[1]
        if self.inCHECK:
            if len(self.Checks) == 1:  # only one check
                moves = self.getValidMoves()
                Check = self.Checks[0]
                CheckRow = Check[0]
                CheckCol = Check[1]
                PieceChecking = self.board[CheckRow][CheckCol]
                ValidSquares = []  # squares available for pieces to move to
                # if N checks king, king must move or N must be captured
                if PieceChecking[1] == "N":
                    ValidSquares = [(CheckRow, CheckCol)]
                else:
                    for i in range(1,8):
                        ValidSquare = (KingRow + Check[2] * i,KingCol + Check[3] * i) #[2] and [3] are the directions
                        ValidSquares.append(ValidSquare)
                        if ValidSquare[0] == CheckRow and ValidSquare[1] == CheckCol:
                            break
                # Remove moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in ValidSquares:
                            moves.remove(moves[i])
            else:  # Double check
                self.KingMoves(KingRow, KingCol, moves)
        else:  # Not in check
            moves = self.getValidMoves()

        if len(moves) == 0:
            if self.inCHECK:
                self.CheckMate = True
            else:
                self.StaleMate = True
        else:
            self.CheckMate = False
            self.StaleMate = False
        return moves

    # All moves without considering checks

    def getValidMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns
                PieceTurn = self.board[r][c][0]
                if (PieceTurn == "w" and self.whiteToMove) or (PieceTurn == "b" and not self.whiteToMove):
                    Piece = self.board[r][c][1]
                    self.MoveFunctions[Piece](r, c, moves)
        return moves

    def PawnMoves(self, r, c, moves):
        PiecePinned = False
        PinDirection = ()
        for i in range(len(self.Pins) - 1, -1, -1):
            if self.Pins[i][0] == r and self.Pins[i][1] == c:
                PiecePinned = True
                PinDirection = (self.Pins[i][2], self.Pins[i][3])
                self.Pins.remove(self.Pins[i])
                break
        if self.whiteToMove:
            MoveAmount = -1
            StartRow = 6
            BackRow = 0
            OppColor = "b"
        else:
            MoveAmount = 1
            StartRow = 1
            BackRow = 7
            OppColor = "w"
        PawnPromotion = False

        if self.board[r+MoveAmount][c] == "--":  # move one square
            if not PiecePinned or PinDirection == (MoveAmount, 0):
                if r +MoveAmount == BackRow:
                    PawnPromotion = True
                moves.append(Move((r,c),(r+MoveAmount, c), self.board, PawnPromotion = PawnPromotion))
                if r == StartRow and self.board[r+2*MoveAmount][c] == "--":  # move 2 squares
                    moves.append(Move((r,c), (r+2*MoveAmount,c), self.board))
        if c - 1 >= 0:  # captures ot the left
            if not PiecePinned or PinDirection == (MoveAmount, -1):
                if self.board[r+MoveAmount][c-1][0] == OppColor:
                    if r + MoveAmount == BackRow:
                        PawnPromotion = True
                    moves.append(Move((r,c), (r+MoveAmount, c-1), self.board, PawnPromotion = PawnPromotion))
                if (r+MoveAmount,c-1) == self.enPassantPossible:
                    moves.append(Move((r,c), (r+MoveAmount, c-1), self.board, enPassantMove=True))
        if c +1 <= 7:  # captures to the right
            if not PiecePinned or PinDirection == (MoveAmount, 1):
                if self.board[r+MoveAmount][c +1][0] == OppColor:
                    if r+MoveAmount == BackRow:
                        PawnPromotion = True
                    moves.append(Move((r,c),(r + MoveAmount, c+1), self.board, PawnPromotion = PawnPromotion))
                if (r + MoveAmount, c + 1) == self.enPassantPossible:
                    moves.append(Move((r,c),(r+MoveAmount,c+1),self.board, enPassantMove=True))


    def RookMoves(self, r,c, moves):
        PiecePinned = False
        PinDirection = ()
        for i in range(len(self.Pins) - 1, -1, -1):
            if self.Pins[i][0] == r and self.Pins[i][1] == c:
                PiecePinned = True
                PinDirection = (self.Pins[i][2], self.Pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.Pins.remove(self.Pins[i])
                break
        directions = ((-1,0),(0, -1),(1,0),(0,1))  # up, left, down, right
        enemypiece = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):  # Rook can move max of 7 squares
                endRow = r + d[0] * i    # !!!
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # instructions within board
                    if not PiecePinned or PinDirection == d or PinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # the space is empty
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemypiece:  # if there is an enemy piece
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                            break
                        else:  # if same color piece
                            break
                else:  # instructions outside board
                    break
    def BishopMoves (self,r,c,moves):
        PiecePinned = False
        PinDirection = ()
        for i in range(len(self.Pins) -1, -1, -1):
            if self.Pins[i][0] == r and self.Pins[i][1] == c:
                PiecePinned = True
                PinDirection = (self.Pins[i][2], (self.Pins[i][3]))
                self.Pins.remove(self.Pins[i])
                break
        directions = ((-1, 1), (-1, -1), (1, 1), (1, -1))  # up/right, up/left, down/right, down/left
        enemypiece = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i  # Continuous until "--"
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # instructions within board
                    if not PiecePinned or PinDirection == d or PinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # the space is empty
                            moves.append(Move((r,c),(endRow,endCol), self.board))
                        elif endPiece[0] == enemypiece:  # if there is an enemy piece
                            moves.append(Move((r,c), (endRow,endCol), self.board))
                            break
                        else:  # if same color piece
                            break
                else:  # instructions outside board
                    break

    def KnightMoves(self, r, c, moves):  # Add pins
        directions = ((-2,-1),(-2,1),(-1,-2),(-1,2),(2,-1),(2,1),(1,-2),(1,2))
        SameTeam = "w" if self.whiteToMove else "b"
        for d in directions:
            endRow = r + d[0]  # knights have a set move. No continuation
            endCol = c + d[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                if self.board[endRow][endCol] != SameTeam or self.board[endRow][endCol] == "--":
                    moves.append(Move((r,c),(endRow,endCol), self.board))

    def QueenMoves(self,r,c,moves):
        self.RookMoves(r,c,moves)
        self.BishopMoves(r,c,moves)

    def KingMoves(self,r,c,moves):
        RowMoves = (-1,-1, -1, 0, 0, 1,1,1)
        ColMoves = (-1, 0, 1, -1, 1, -1, 0,1)
        SameTeam = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + RowMoves[i]
            endCol = c + ColMoves[i]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # complete: unable to capture same colour piece
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != SameTeam:
                    if SameTeam == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCHECK, Pins, Checks = self.FindPinsandChecks()
                    if not inCHECK:
                        moves.append(Move((r,c), (endRow,endCol), self.board))
                    if SameTeam == "w":
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)
        self.CastleMoves(r,c,moves, SameTeam)

    def inCHECK(self):
        if self.whiteToMove:
            return self.SquareunderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        if not self.whiteToMove:
            return self.SquareunderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def CastleMoves(self, r,c,moves, SameTeam):
        # if self.SquareunderAttack(r,c):
           # return # unable to castle while in Check
        if (self.whiteToMove and self.CastlingNow.wks) or (not self.whiteToMove and self.CastlingNow.bks):
            self.KingsideCastle(r,c,moves)
        if (self.whiteToMove and self.CastlingNow.wqs) or (not self.whiteToMove and self.CastlingNow.bqs):
            self.QueensideCastle(r, c, moves)

    def KingsideCastle (self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.SquareunderAttack(r,c+1) and not self.SquareunderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2), self.board, Castle = True ))


    def QueensideCastle(self,r,c,moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3]:
            if not self.SquareunderAttack(r,c-1) and not self.SquareunderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2), self.board, Castle = True ))



    def SquareunderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        OppMoves = self.legalMoves()
        self.whiteToMove = not self.whiteToMove
        for move in OppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    # If the King is in check, pins and checks
    def FindPinsandChecks(self):
        Pins = []  # square pinned piece is // Where the check is coming from
        Checks = [] # square where enemy is checking from
        inCHECK = False
        #initializing(assigning 1st time) variables based on player sides
        if self.whiteToMove:
            OppColor = "b"
            SameColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            OppColor = "w"
            SameColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # keep track of pins / Check for pins and checks
        # Checking all squares around the king
        directions = ((-1,0), (0,-1), (1,0), (0, 1), (-1,-1), (-1,1), (1, -1), (1, 1))
        for g in range(len(directions)):
            d = directions[g]
            PossiblePin = ()  # reset all possible pins
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # ensure piece is within the board(/ not out of bounds)
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == SameColor and endPiece[1] != "K":
                        if PossiblePin == ():
                            PossiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == OppColor:
                        type = endPiece[1]
                        if (0 <= g <= 3 and type == "R") or \
                                (4 <= g <= 7 and type == "B") or \
                                (i == 1 and type == "p" and ((OppColor == "w" and 6 <= g <= 7) or (OppColor == "b" and
                                                                                                  4 <= g <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            if PossiblePin == (): #King in Check
                                inCHECK = True
                                Checks.append((endRow,endCol, d[0], d[1]))
                                break
                            else: #Piece Pinned
                                Pins.append(PossiblePin)
                                break
                        else:  # Opposite piece not having the king in check
                            break
                else:  # Off board
                    break
        #  Knight Checks
        KnightMoves = ((-2,-1),(-1,-2),(1,-2),(2,-1),(2,1),(1,2),(-1,2),(-2,1))
        for m in KnightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == OppColor and endPiece[1] == "N":  # Opp Knight attacking king
                    inCHECK = True
                    Checks.append((endRow, endCol, m[0], m[1]))
        return inCHECK, Pins, Checks

    def CastlingRights(self,move): # update castling rights
        if move.pieceMoved == "wK":
            self.CastlingNow.wqs = False
            self.CastlingNow.wks = False
        elif move.pieceMoved == "bK":
            self.CastlingNow.bqs = False
            self.CastlingNow.bks = False
        elif move.pieceMoved == "wR":
            if move.startRow ==7:
                if move.startCol ==7: # Right rook
                    self.CastlingNow.wks = False
                elif move.startCol ==0: # left rook
                    self.CastlingNow.wqs = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol ==7: # right rook
                    self.CastlingNow.bks = False
                elif move.startCol ==0: # left rook
                    self.CastlingNow.bqs = False

    def returnPiece(self, position):
        row = position[0]
        col = position[1]
        return self.board[row][col]
class CastleRights(): # castle rights
    def __init__(self, wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

# Let's create a move class
class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}  # opposite of ranksToRows
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassantMove=False, PawnPromotion=False, Castle = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.PawnPromotion = PawnPromotion
        self.enPassantmove = enPassantMove
        self.Castle = Castle
        #  enPassant
        if enPassantMove:
            self.pieceCaptured = "bp" if self.pieceMoved == "wp" else "wp"
        #  Pawn Promotion to Queen only
        self.PawnPromotion = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7):
            self.PawnPromotion = True

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        print(self.moveID)


    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        print(self.colsToFiles)
        print(self.rowsToRanks)
        return self.colsToFiles[c] + self.rowsToRanks[r]
