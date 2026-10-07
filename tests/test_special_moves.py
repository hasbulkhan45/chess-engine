import unittest
from engine.board import Board
from engine.move import Move
from pieces.queen import Queen
from pieces.rook import Rook
from pieces.bishop import Bishop
from pieces.knight import Knight


class TestSpecialMoves(unittest.TestCase):
    def test_white_kingside_castling(self):
        # Position where White kingside castling is legal
        b = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1")
        # Empty f1, g1
        b.board[7, 5] = None
        b.board[7, 6] = None
        legal_moves = b.get_legal_moves("white")
        castle_move = [m for m in legal_moves if m.is_castling and m.end_col == 6]
        self.assertTrue(len(castle_move) == 1)

        # Make move
        b.make_move(castle_move[0])
        # King on g1 (7, 6), Rook on f1 (7, 5)
        self.assertEqual(b.board[7, 6].piece_type, "k")
        self.assertEqual(b.board[7, 5].piece_type, "r")
        self.assertIsNone(b.board[7, 4])
        self.assertIsNone(b.board[7, 7])

        # Undo move
        b.undo_move()
        self.assertEqual(b.board[7, 4].piece_type, "k")
        self.assertEqual(b.board[7, 7].piece_type, "r")
        self.assertIsNone(b.board[7, 6])
        self.assertIsNone(b.board[7, 5])

    def test_castling_blocked_by_check(self):
        # White king in check cannot castle
        b = Board("r3k2r/8/8/8/8/8/8/R3K2r w Qkq - 0 1")
        legal_moves = b.get_legal_moves("white")
        castle_moves = [m for m in legal_moves if m.is_castling]
        self.assertEqual(len(castle_moves), 0)

    def test_castling_through_check(self):
        # Rook attacks f1, so White cannot castle kingside through check
        b = Board("4k2r/8/8/8/8/5r2/8/R3K2R w KQk - 0 1")
        legal_moves = b.get_legal_moves("white")
        kingside_castle = [m for m in legal_moves if m.is_castling and m.end_col == 6]
        self.assertEqual(len(kingside_castle), 0)

    def test_en_passant(self):
        # 1. e4 e6 2. e5 d5 3. exd6 (en passant)
        b = Board()
        b.make_move("e2e4")
        b.make_move("e7e6")
        b.make_move("e4e5")
        b.make_move("d7d5")  # Black pawn moves 2 squares, setting ep target to d6 (2, 3)

        self.assertEqual(b.en_passant_target, (2, 3))
        legal_moves = b.get_legal_moves("white")
        ep_moves = [m for m in legal_moves if m.is_en_passant]
        self.assertEqual(len(ep_moves), 1)

        # Execute en passant
        b.make_move("e5d6")
        self.assertIsNone(b.board[3, 3])  # Black pawn on d5 should be captured!
        self.assertEqual(b.board[2, 3].piece_type, "p")
        self.assertEqual(b.board[2, 3].color, "white")

        # Undo en passant
        b.undo_move()
        self.assertEqual(b.board[3, 3].piece_type, "p")
        self.assertEqual(b.board[3, 3].color, "black")
        self.assertEqual(b.board[3, 4].piece_type, "p")
        self.assertEqual(b.board[3, 4].color, "white")

    def test_pawn_promotion(self):
        # White pawn on a7 (1, 0) about to promote to a8 (0, 0)
        b = Board("8/P7/8/8/8/8/8/4K2k w - - 0 1")
        legal_moves = b.get_legal_moves("white")
        promo_moves = [m for m in legal_moves if m.promotion is not None]
        self.assertEqual(len(promo_moves), 4)  # Q, R, B, N

        # Promote to Queen
        b.make_move("a7a8q")
        self.assertIsInstance(b.board[0, 0], Queen)
        self.assertEqual(b.board[0, 0].color, "white")

        # Undo promotion
        b.undo_move()
        self.assertEqual(b.board[1, 0].piece_type, "p")
        self.assertIsNone(b.board[0, 0])

        # Promote to Knight
        b.make_move("a7a8n")
        self.assertIsInstance(b.board[0, 0], Knight)


if __name__ == "__main__":
    unittest.main()
