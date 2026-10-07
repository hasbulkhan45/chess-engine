from engine.piece import Piece


class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_type = "k"
        self.value = 20000

    def __str__(self):
        if self.color == "black":
            return "k"
        else:
            return "K"

    def get_moves(self, board, row, col):
        moves = []
        offsets = [
            (1, 0), (-1, 0),
            (0, 1), (0, -1),
            (1, -1), (1, 1),
            (-1, 1), (-1, -1)
        ]

        for dr, dc in offsets:
            new_row = row + dr
            new_col = col + dc

            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = board[new_row, new_col]
                if piece is None or piece.color != self.color:
                    moves.append((new_row, new_col))

        return moves