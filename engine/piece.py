class Piece:
    def __init__(self,color):
        self.color=color
        self.is_moved=False
    def __str__(self):
        return "?"
    def get_moves(self,board,row,col):
        raise NotImplementedError