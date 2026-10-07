import random

# Fixed seed for consistent hashes across sessions
_rng = random.Random(42)

# Piece keys: 2 colors ('white', 'black') x 6 piece types ('p', 'n', 'b', 'r', 'q', 'k') x 64 squares
PIECE_KEYS = {}
for color in ("white", "black"):
    PIECE_KEYS[color] = {}
    for pt in ("p", "n", "b", "r", "q", "k"):
        PIECE_KEYS[color][pt] = [_rng.getrandbits(64) for _ in range(64)]

# Side to move (XOR if black's turn)
SIDE_KEY = _rng.getrandbits(64)

# Castling keys: 16 combinations (binary flags for K, Q, k, q)
CASTLE_KEYS = [_rng.getrandbits(64) for _ in range(16)]

# En passant keys: 8 files (a-h) + 1 for no EP
EP_KEYS = [_rng.getrandbits(64) for _ in range(8)]


def castle_rights_to_index(castling_rights):
    """Converts a castling rights dict to a 0-15 bitmask integer."""
    idx = 0
    if castling_rights.get("K", False):
        idx |= 1
    if castling_rights.get("Q", False):
        idx |= 2
    if castling_rights.get("k", False):
        idx |= 4
    if castling_rights.get("q", False):
        idx |= 8
    return idx


def compute_board_hash(board):
    """Computes the full 64-bit Zobrist hash for a given Board instance."""
    h = 0

    # Pieces
    for r in range(8):
        for c in range(8):
            piece = board.board[r, c]
            if piece is not None:
                pt = getattr(piece, "piece_type", None)
                if pt in PIECE_KEYS.get(piece.color, {}):
                    h ^= PIECE_KEYS[piece.color][pt][r * 8 + c]

    # Side to move
    if board.turn == "black":
        h ^= SIDE_KEY

    # Castling rights
    c_idx = castle_rights_to_index(board.castling_rights)
    h ^= CASTLE_KEYS[c_idx]

    # En passant target
    if board.en_passant_target is not None:
        _, ep_col = board.en_passant_target
        if 0 <= ep_col < 8:
            h ^= EP_KEYS[ep_col]

    return h
