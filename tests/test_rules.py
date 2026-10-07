import unittest
from engine.board import Board


class TestRules(unittest.TestCase):
    def test_fools_mate(self):
        # 1. f3 e5 2. g4 Qh4# (Fool's Mate)
        b = Board()
        b.make_move("f2f3")
        b.make_move("e7e5")
        b.make_move("g2g4")
        b.make_move("d8h4")

        self.assertTrue(b.is_in_check("white"))
        self.assertTrue(b.is_checkmate("white"))
        self.assertFalse(b.is_stalemate("white"))
        status, winner = b.get_game_status()
        self.assertEqual(status, "checkmate")
        self.assertEqual(winner, "black")

    def test_scholars_mate(self):
        # 1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7#
        b = Board()
        b.make_move("e2e4")
        b.make_move("e7e5")
        b.make_move("d1h5")
        b.make_move("b8c6")
        b.make_move("f1c4")
        b.make_move("g8f6")
        b.make_move("h5f7")

        self.assertTrue(b.is_in_check("black"))
        self.assertTrue(b.is_checkmate("black"))
        status, winner = b.get_game_status()
        self.assertEqual(status, "checkmate")
        self.assertEqual(winner, "white")

    def test_stalemate(self):
        # Classic stalemate position: Black king on a8, White queen on c7, White king on c8
        b = Board("k7/2Q5/2K5/8/8/8/8/8 b - - 0 1")
        self.assertFalse(b.is_in_check("black"))
        self.assertTrue(b.is_stalemate("black"))
        self.assertFalse(b.is_checkmate("black"))
        status, winner = b.get_game_status()
        self.assertEqual(status, "stalemate")
        self.assertIsNone(winner)

    def test_insufficient_material(self):
        # K vs K
        b1 = Board("8/8/8/4k3/8/8/4K3/8 w - - 0 1")
        self.assertTrue(b1.is_insufficient_material())

        # K + B vs K
        b2 = Board("8/8/8/4k3/8/2B5/4K3/8 w - - 0 1")
        self.assertTrue(b2.is_insufficient_material())

        # K + N vs K
        b3 = Board("8/8/8/4k3/8/2N5/4K3/8 w - - 0 1")
        self.assertTrue(b3.is_insufficient_material())

        # K + P vs K (sufficient because pawn can promote)
        b4 = Board("8/8/8/4k3/8/2P5/4K3/8 w - - 0 1")
        self.assertFalse(b4.is_insufficient_material())

    def test_fifty_move_rule(self):
        b = Board()
        b.halfmove_clock = 100
        self.assertTrue(b.is_fifty_moves())
        self.assertTrue(b.is_game_over())

    def test_threefold_repetition(self):
        # Knights bouncing back and forth
        b = Board()
        # 1. Nf3 Nf6 2. Ng1 Ng8 (1 repetition)
        b.make_move("g1f3")
        b.make_move("g8f6")
        b.make_move("f3g1")
        b.make_move("f6g8")

        # 3. Nf3 Nf6 4. Ng1 Ng8 (2nd repetition)
        b.make_move("g1f3")
        b.make_move("g8f6")
        b.make_move("f3g1")
        b.make_move("f6g8")

        self.assertTrue(b.is_threefold_repetition())
        self.assertTrue(b.is_game_over())


if __name__ == "__main__":
    unittest.main()
