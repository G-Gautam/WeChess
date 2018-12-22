# Constants
BUFFER_SIZE = 1024

class ROLE:
    WHITE = "W"
    BLACK = "B"
    SPECTATOR = "S"

class PIECE:
    EMPTY = "."
    W_KING = "k"
    W_QUEEN = "q"
    W_ROOK = "r"
    W_BISHOP = "b"
    W_KNIGHT = "n"
    W_PAWN = "p"
    B_KING = "K"
    B_QUEEN = "Q"
    B_ROOK = "R"
    B_BISHOP = "B"
    B_KNIGHT = "N"
    B_PAWN = "P"

class M_TYPE:
    CHAT = "CHAT"
    CHESS = "CHESS"
    EVENT = "EVENT"

class EVENT:
    LEAVE = "LEAVE"