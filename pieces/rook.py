from engine.piece import Piece


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.piece_type = "r"
        self.value = 500

    def __str__(self):
        if self.color == "black":
            return "r"
        else:
            return "R"

    def get_moves(self, board, row, col):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            while 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = board[new_row, new_col]
                if piece is None:
                    moves.append((new_row, new_col))
                elif piece.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
                new_row += dr
                new_col += dc
        return moves