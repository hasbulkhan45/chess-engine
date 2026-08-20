import numpy as np
from engine.piece import Piece
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
        self.turn="white"
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
    def make_move(self,start_row,start_col,end_row,end_col):
        piece=self.board[start_row,start_col]
        captured_piece=self.board[end_row,end_col]

        if piece is None:
            print(f"No piece selected")
            return False
        if piece.color != self.turn:
            print(f"It's {self.turn}'s turn")
            return False
        legal_moves=piece.get_moves(self.board,start_row,start_col)

        if (end_row,end_col) not in legal_moves:
            print("Illegal Move")
            return False
        self.board[end_row,end_col]=piece
        self.board[start_row,start_col]=None

        if self.is_in_check(piece.color):
            self.board[start_row, start_col] = piece
            self.board[end_row, end_col] = captured_piece
            print("Move leaves king in check")
            return False
        piece.is_moved = True
        if self.turn == "white":
            self.turn = "black"
        else:
            self.turn = "white"

        return True

    def is_in_check(self, color):
        all_moves = []
        pieces = []
        my_king = None

        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]

                
                if isinstance(piece, Pawn) and piece.color != color:
                    direction = 1 if piece.color == "black" else -1
                    new_row = row + direction

                    if 0 <= new_row < 8:
                        if 0 <= col - 1 < 8:
                            all_moves.append((new_row, col - 1))

                        if 0 <= col + 1 < 8:
                            all_moves.append((new_row, col + 1))

                
                elif piece is not None and piece.color != color:
                    pieces.append((piece, row, col))

                
                elif isinstance(piece, King) and piece.color == color:
                    my_king = (row, col)

        
        for piece, row, col in pieces:
            moves = piece.get_moves(self.board, row, col)

            for move in moves:
                all_moves.append(move)

        return my_king in all_moves
    
    def checkmate(self, color):

        # If the king isn't currently in check,
        # it cannot be checkmate.
        if not self.is_in_check(color):
            return False

        pieces = []

        # Find every piece belonging to the player in check
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]

                if piece is not None and piece.color == color:
                    pieces.append((piece, row, col))

        # Try every possible move of every piece
        for piece, start_row, start_col in pieces:

            moves = piece.get_moves(
                self.board,
                start_row,
                start_col
            )

            for end_row, end_col in moves:

                # Save whatever is currently on the destination
                captured_piece = self.board[end_row, end_col]

                # Temporarily make the move
                self.board[end_row, end_col] = piece
                self.board[start_row, start_col] = None

                # Check whether this move gets the king out of check
                still_in_check = self.is_in_check(color)

                # Undo the temporary move
                self.board[start_row, start_col] = piece
                self.board[end_row, end_col] = captured_piece

                # If even ONE move saves the king,
                # it isn't checkmate.
                if not still_in_check:
                    return False

        # We were in check and no move could save the king
        return True