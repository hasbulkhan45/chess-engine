from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.queen import Queen
from pieces.rook import Rook

# Piece base values (in centipawns)
PIECE_VALUES = {
    "p": 100,
    "n": 320,
    "b": 330,
    "r": 500,
    "q": 900,
    "k": 20000,
}

# Phase weights for tapered evaluation
PHASE_WEIGHTS = {
    "p": 0,
    "n": 1,
    "b": 1,
    "r": 2,
    "q": 4,
    "k": 0,
}
TOTAL_PHASE = 24  # 4 knights (4) + 4 bishops (4) + 4 rooks (8) + 2 queens (8)

# Piece-Square Tables (White perspective, rank 8 to rank 1, row 0 = rank 8, row 7 = rank 1)
# For Black, row is mirrored: (7 - row)

PAWN_TABLE_MG = [
    [  0,   0,   0,   0,   0,   0,   0,   0],
    [ 50,  50,  50,  50,  50,  50,  50,  50],
    [ 10,  10,  20,  30,  30,  20,  10,  10],
    [  5,   5,  10,  25,  25,  10,   5,   5],
    [  0,   0,   0,  20,  20,   0,   0,   0],
    [  5,  -5, -10,   0,   0, -10,  -5,   5],
    [  5,  10,  10, -20, -20,  10,  10,   5],
    [  0,   0,   0,   0,   0,   0,   0,   0],
]

PAWN_TABLE_EG = [
    [  0,   0,   0,   0,   0,   0,   0,   0],
    [ 80,  80,  80,  80,  80,  80,  80,  80],
    [ 50,  50,  50,  50,  50,  50,  50,  50],
    [ 30,  30,  30,  30,  30,  30,  30,  30],
    [ 20,  20,  20,  20,  20,  20,  20,  20],
    [ 10,  10,  10,  10,  10,  10,  10,  10],
    [  5,   5,   5,   5,   5,   5,   5,   5],
    [  0,   0,   0,   0,   0,   0,   0,   0],
]

KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20,   0,   0,   0,   0, -20, -40],
    [-30,   0,  10,  15,  15,  10,   0, -30],
    [-30,   5,  15,  20,  20,  15,   5, -30],
    [-30,   0,  15,  20,  20,  15,   0, -30],
    [-30,   5,  10,  15,  15,  10,   5, -30],
    [-40, -20,   0,   5,   5,   0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50],
]

BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,  10,  10,   5,   0, -10],
    [-10,   5,   5,  10,  10,   5,   5, -10],
    [-10,   0,  10,  10,  10,  10,   0, -10],
    [-10,  10,  10,  10,  10,  10,  10, -10],
    [-10,   5,   0,   0,   0,   0,   5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20],
]

ROOK_TABLE = [
    [  0,   0,   0,   0,   0,   0,   0,   0],
    [  5,  10,  10,  10,  10,  10,  10,   5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [ -5,   0,   0,   0,   0,   0,   0,  -5],
    [  0,   0,   0,   5,   5,   0,   0,   0],
]

QUEEN_TABLE = [
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
    [-10,   0,   0,   0,   0,   0,   0, -10],
    [-10,   0,   5,   5,   5,   5,   0, -10],
    [ -5,   0,   5,   5,   5,   5,   0,  -5],
    [  0,   0,   5,   5,   5,   5,   0,  -5],
    [-10,   5,   5,   5,   5,   5,   0, -10],
    [-10,   0,   5,   0,   0,   0,   0, -10],
    [-20, -10, -10,  -5,  -5, -10, -10, -20],
]

KING_TABLE_MG = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -20, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [ 20,  20,   0,   0,   0,   0,  20,  20],
    [ 20,  30,  10,   0,   0,  10,  30,  20],
]

KING_TABLE_EG = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10,   0,   0, -10, -20, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  30,  40,  40,  30, -10, -30],
    [-30, -10,  20,  30,  30,  20, -10, -30],
    [-30, -30,   0,   0,   0,   0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50],
]


def evaluate_board(board, perspective="turn"):
    """
    Evaluates the board position.
    Returns centipawns:
    - If perspective == 'turn': positive means good for side to move.
    - If perspective == 'white': positive means good for White, negative for Black.
    """
    # Quick terminal state checks
    if board.is_checkmate(board.turn):
        return -200000 if perspective == "turn" else (-200000 if board.turn == "white" else 200000)
    if board.is_stalemate(board.turn) or board.is_insufficient_material() or board.is_fifty_moves():
        return 0

    mg_score = [0, 0]  # [white, black]
    eg_score = [0, 0]  # [white, black]
    game_phase = 0

    white_bishops = 0
    black_bishops = 0
    white_pawns = [[] for _ in range(8)]  # pawns by column
    black_pawns = [[] for _ in range(8)]

    for r in range(8):
        for c in range(8):
            piece = board.board[r, c]
            if piece is None:
                continue

            color_idx = 0 if piece.color == "white" else 1
            pt = getattr(piece, "piece_type", "p")
            val = PIECE_VALUES.get(pt, 0)

            # Update game phase
            game_phase += PHASE_WEIGHTS.get(pt, 0)

            # Mirror row for black
            table_r = r if piece.color == "white" else (7 - r)

            if pt == "p":
                mg = val + PAWN_TABLE_MG[table_r][c]
                eg = val + PAWN_TABLE_EG[table_r][c]
                if piece.color == "white":
                    white_pawns[c].append(r)
                else:
                    black_pawns[c].append(r)
            elif pt == "n":
                pst = KNIGHT_TABLE[table_r][c]
                mg = val + pst
                eg = val + pst
            elif pt == "b":
                pst = BISHOP_TABLE[table_r][c]
                mg = val + pst
                eg = val + pst
                if piece.color == "white":
                    white_bishops += 1
                else:
                    black_bishops += 1
            elif pt == "r":
                pst = ROOK_TABLE[table_r][c]
                mg = val + pst
                eg = val + pst
            elif pt == "q":
                pst = QUEEN_TABLE[table_r][c]
                mg = val + pst
                eg = val + pst
            elif pt == "k":
                mg = val + KING_TABLE_MG[table_r][c]
                eg = val + KING_TABLE_EG[table_r][c]
            else:
                mg = val
                eg = val

            mg_score[color_idx] += mg
            eg_score[color_idx] += eg

    # Bishop pair bonus
    if white_bishops >= 2:
        mg_score[0] += 35
        eg_score[0] += 35
    if black_bishops >= 2:
        mg_score[1] += 35
        eg_score[1] += 35

    # Pawn structure evaluation
    for col in range(8):
        # Doubled pawns penalty
        if len(white_pawns[col]) > 1:
            mg_score[0] -= 20 * (len(white_pawns[col]) - 1)
            eg_score[0] -= 20 * (len(white_pawns[col]) - 1)
        if len(black_pawns[col]) > 1:
            mg_score[1] -= 20 * (len(black_pawns[col]) - 1)
            eg_score[1] -= 20 * (len(black_pawns[col]) - 1)

        # Isolated pawns penalty
        if white_pawns[col]:
            left = white_pawns[col - 1] if col > 0 else []
            right = white_pawns[col + 1] if col < 7 else []
            if not left and not right:
                mg_score[0] -= 15
                eg_score[0] -= 15

        if black_pawns[col]:
            left = black_pawns[col - 1] if col > 0 else []
            right = black_pawns[col + 1] if col < 7 else []
            if not left and not right:
                mg_score[1] -= 15
                eg_score[1] -= 15

    # Interpolate middle-game and end-game scores
    mg_diff = mg_score[0] - mg_score[1]
    eg_diff = eg_score[0] - eg_score[1]

    phase = min(game_phase, TOTAL_PHASE)
    white_score = (mg_diff * phase + eg_diff * (TOTAL_PHASE - phase)) // TOTAL_PHASE

    if perspective == "white":
        return white_score
    else:
        return white_score if board.turn == "white" else -white_score
