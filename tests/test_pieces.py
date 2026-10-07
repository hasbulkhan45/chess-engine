import unittest
from engine.board import Board
from pieces.pawn import Pawn
from pieces.knight import Knight
from pieces.bishop import Bishop
from pieces.rook import Rook
from pieces.queen import Queen
from pieces.king import King


class TestPieces(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_pawn_initial_moves(self):
        # White pawn on e2 (6, 4) should have 2 moves: e3 (5, 4) and e4 (4, 4)
        pawn = self.board.board[6, 4]
        moves = pawn.get_moves(self.board, 6, 4)
        self.assertIn((5, 4), moves)
        self.assertIn((4, 4), moves)
        self.assertEqual(len(moves), 2)

    def test_knight_moves(self):
        # White knight on b1 (7, 1) has 2 moves at start: a3 (5, 0) and c3 (5, 2)
        knight = self.board.board[7, 1]
        moves = knight.get_moves(self.board, 7, 1)
        self.assertEqual(len(moves), 2)
        self.assertIn((5, 0), moves)
        self.assertIn((5, 2), moves)

    def test_bishop_blocked_at_start(self):
        # White bishop on c1 (7, 2) blocked by pawns
        bishop = self.board.board[7, 2]
        moves = bishop.get_moves(self.board, 7, 2)
        self.assertEqual(len(moves), 0)

    def test_rook_blocked_at_start(self):
        # White rook on a1 (7, 0) blocked by pawns/knights
        rook = self.board.board[7, 0]
        moves = rook.get_moves(self.board, 7, 0)
        self.assertEqual(len(moves), 0)

    def test_queen_moves_after_e4(self):
        # 1. e4 opens diagonal for White Queen (7, 3) -> (6, 4), (5, 5), (4, 6), (3, 7)
        self.board.make_move("e2e4")
        queen = self.board.board[7, 3]
        moves = queen.get_moves(self.board, 7, 3)
        self.assertIn((6, 4), moves)
        self.assertIn((5, 5), moves)
        self.assertIn((4, 6), moves)
        self.assertIn((3, 7), moves)

    def test_king_moves(self):
        # Board with lone king in center
        b = Board("8/8/8/4K3/8/8/8/8 w - - 0 1")
        king = b.board[3, 4]
        moves = king.get_moves(b, 3, 4)
        self.assertEqual(len(moves), 8)


if __name__ == "__main__":
    unittest.main()
