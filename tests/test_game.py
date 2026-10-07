import unittest
from engine.game import Game, GameStatus


class TestGame(unittest.TestCase):
    def test_game_flow_and_pgn(self):
        g = Game()
        self.assertEqual(g.status, GameStatus.IN_PROGRESS)

        # Play Scholar's mate
        g.play_move("e2e4")
        g.play_move("e7e5")
        g.play_move("d1h5")
        g.play_move("b8c6")
        g.play_move("f1c4")
        g.play_move("g8f6")
        g.play_move("h5f7")

        self.assertTrue(g.is_over())
        self.assertEqual(g.status, GameStatus.CHECKMATE)
        self.assertEqual(g.winner, "white")

        pgn = g.export_pgn(white="Alice", black="Bob")
        self.assertIn('[White "Alice"]', pgn)
        self.assertIn('[Black "Bob"]', pgn)
        self.assertIn('[Result "1-0"]', pgn)
        self.assertIn("1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7# 1-0", pgn)

    def test_undo_and_redo(self):
        g = Game()
        g.play_move("e2e4")
        self.assertEqual(len(g.history), 1)

        g.undo_move()
        self.assertEqual(len(g.history), 0)
        self.assertEqual(g.board.turn, "white")
        self.assertEqual(len(g.redo_stack), 1)

        g.redo_move()
        self.assertEqual(len(g.history), 1)
        self.assertEqual(g.board.turn, "black")
        self.assertEqual(len(g.redo_stack), 0)


if __name__ == "__main__":
    unittest.main()
