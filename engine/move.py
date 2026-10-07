def square_to_str(row, col):
    """Converts (row, col) (0-7, 0-7) to algebraic notation (e.g., (7, 4) -> 'e1')."""
    return f"{chr(ord('a') + col)}{8 - row}"


def str_to_square(sq_str):
    """Converts algebraic notation (e.g., 'e4') to (row, col) (0-7, 0-7)."""
    sq_str = sq_str.strip().lower()
    if len(sq_str) < 2:
        raise ValueError(f"Invalid square notation: '{sq_str}'")
    col = ord(sq_str[0]) - ord('a')
    row = 8 - int(sq_str[1])
    if not (0 <= row < 8 and 0 <= col < 8):
        raise ValueError(f"Square out of bounds: '{sq_str}'")
    return (row, col)


class Move:
    def __init__(self, start_pos, end_pos, piece_moved=None, piece_captured=None,
                 promotion=None, is_castling=False, is_en_passant=False):
        self.start_row, self.start_col = start_pos
        self.end_row, self.end_col = end_pos
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.promotion = promotion.lower() if isinstance(promotion, str) else promotion
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant

    @property
    def start_square(self):
        return (self.start_row, self.start_col)

    @property
    def end_square(self):
        return (self.end_row, self.end_col)

    def uci(self):
        start_sq = square_to_str(self.start_row, self.start_col)
        end_sq = square_to_str(self.end_row, self.end_col)
        promo = f"{self.promotion}".lower() if self.promotion else ""
        return f"{start_sq}{end_sq}{promo}"

    @classmethod
    def from_uci(cls, uci_str, board=None):
        uci_str = uci_str.strip().lower()
        if len(uci_str) < 4:
            raise ValueError(f"Invalid UCI move string: '{uci_str}'")
        start_sq = str_to_square(uci_str[:2])
        end_sq = str_to_square(uci_str[2:4])
        promotion = uci_str[4] if len(uci_str) > 4 else None

        piece_moved = None
        piece_captured = None
        is_castling = False
        is_en_passant = False

        if board is not None:
            piece_moved = board[start_sq[0], start_sq[1]]
            piece_captured = board[end_sq[0], end_sq[1]]
            # Check castling
            if piece_moved and getattr(piece_moved, 'piece_type', None) == 'k':
                if abs(start_sq[1] - end_sq[1]) == 2:
                    is_castling = True
            # Check en passant
            if piece_moved and getattr(piece_moved, 'piece_type', None) == 'p':
                ep = getattr(board, 'en_passant_target', None)
                if ep == end_sq and piece_captured is None:
                    is_en_passant = True

        return cls(start_sq, end_sq, piece_moved, piece_captured,
                   promotion=promotion, is_castling=is_castling, is_en_passant=is_en_passant)

    def __eq__(self, other):
        if isinstance(other, Move):
            return (self.start_row == other.start_row and
                    self.start_col == other.start_col and
                    self.end_row == other.end_row and
                    self.end_col == other.end_col and
                    self.promotion == other.promotion)
        elif isinstance(other, tuple):
            if len(other) == 2:
                if isinstance(other[0], tuple):
                    return (self.start_square == other[0] and self.end_square == other[1])
                elif isinstance(other[0], int):
                    return self.end_square == other
        elif isinstance(other, str):
            return self.uci() == other.lower()
        return False

    def __hash__(self):
        return hash((self.start_row, self.start_col, self.end_row, self.end_col, self.promotion))

    def __str__(self):
        return self.uci()

    def __repr__(self):
        return f"Move({self.uci()})"
