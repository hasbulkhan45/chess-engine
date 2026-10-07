from engine.piece import Piece


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_type = "p"
        self.value = 100

    def __str__(self):
        if self.color == "black":
            return "p"
        else:
            return "P"

    def get_moves(self, board, row, col):
        moves = []
        direction = 1 if self.color == "black" else -1
        start_row = 1 if self.color == "black" else 6

        # Single step forward
        new_row = row + direction
        if 0 <= new_row < 8 and board[new_row, col] is None:
            moves.append((new_row, col))

            # Double step forward from initial rank
            if not self.is_moved and row == start_row:
                double_row = row + 2 * direction
                if 0 <= double_row < 8 and board[double_row, col] is None:
                    moves.append((double_row, col))

        # Diagonal captures & en passant
        if 0 <= new_row < 8:
            ep = getattr(board, "en_passant_target", None)
            for dc in (-1, 1):
                new_col = col + dc
                if 0 <= new_col < 8:
                    piece = board[new_row, new_col]
                    if piece is not None and piece.color != self.color:
                        moves.append((new_row, new_col))
                    elif ep is not None and (new_row, new_col) == ep:
                        moves.append((new_row, new_col))

        return moves