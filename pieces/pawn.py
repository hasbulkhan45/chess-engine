from engine.piece import Piece

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        if self.color == "black":
            return "p"
        else:
            return "P"

    def get_moves(self, board, row, col):
        moves = []

        if self.color == "black":
            direction = 1
        else:
            direction = -1

        # One square forward
        new_row = row + direction
        if 0 <= new_row < 8 and board[new_row, col] is None:
            moves.append((new_row, col))

            # Two squares forward on first move
            if self.is_moved == False:
                new_row = row + 2 * direction
                if 0 <= new_row < 8 and board[new_row, col] is None:
                    moves.append((new_row, col))

        # Reset new_row for captures
        new_row = row + direction

        # Capture right
        if 0 <= col + 1 < 8:
            piece = board[new_row, col + 1]
            if piece and piece.color != self.color:
                moves.append((new_row, col + 1))

        # Capture left
        if 0 <= col - 1 < 8:
            piece = board[new_row, col - 1]
            if piece and piece.color != self.color:
                moves.append((new_row, col - 1))

        return moves