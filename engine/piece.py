class Piece:
    def __init__(self, color):
        self.color = color
        self.is_moved = False
        self.piece_type = ""
        self.value = 0

    def __str__(self):
        return "?"

    def __repr__(self):
        return self.__str__()

    def get_moves(self, board, row, col):
        raise NotImplementedError

    def copy(self):
        cls = self.__class__
        new_piece = cls(self.color)
        new_piece.is_moved = self.is_moved
        return new_piece