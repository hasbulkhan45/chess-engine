import numpy as np
from pieces.pawn import Pawn
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.queen import Queen
from pieces.king import King
class Board:
    def __init__(self):
        self.board=np.full((8,8),None, dtype=object)
        self.setup()
    def setup(self):
        for i in range(8):
            self.board[1, i] = Pawn("black")
        for i in range(8):
            self.board[6, i] = Pawn("white")
        pieces = [Rook,Knight,Bishop,Queen,King,Bishop,Knight,Rook]
        for i in range(8):
            self.board[0,i]=pieces[i]("black")
        for i in range(8):
            self.board[7,i]=pieces[i]("white")
    def __str__(self):
        output=""
        for row in self.board:
            for cell in row:
                if cell is None:
                    output+=". "
                else:
                    output+=f"{cell} "
            output+="\n"
        return output