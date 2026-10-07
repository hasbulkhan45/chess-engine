from engine.piece import Piece


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_type = "n"
        self.value = 320

    def __str__(self):
        if self.color == "black":
            return "n"
        else:
            return "N"

    def get_moves(self, board, row, col):
        offsets = [
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        ]
        moves = []
        for dr, dc in offsets:
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = board[new_row, new_col]
                if piece is None or piece.color != self.color:
                    moves.append((new_row, new_col))
        return moves
