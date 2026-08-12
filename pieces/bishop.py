from engine.piece import Piece

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)

    def __str__(self):
        if self.color=="black":
            return "b"
        else:
            return "B"

    def get_moves(self, board, row, col):
        moves=[]
        direction=[(1,1),(-1,-1),(1,-1),(-1,1)]
        for dr,dc in direction:
            new_row=row+dr
            new_col=col+dc

            while 0<=new_row<8 and 0<=new_col<8:
                piece=board[new_row,new_col]

                if piece is None:
                    moves.append((new_row,new_col))
                elif piece.color!=self.color:
                    moves.append((new_row,new_col))
                    break
                else:
                    break
                new_row+=dr
                new_col+=dc
        return moves