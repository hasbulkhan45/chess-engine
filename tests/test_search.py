import unittest
from engine.board import Board
from engine.search import SearchEngine
from engine.evaluation import evaluate_board


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.engine = SearchEngine()

    def test_initial_eval_symmetric(self):
        b = Board()
        score = evaluate_board(b, perspective="white")
        # Starting position should be perfectly symmetric (score 0)
        self.assertEqual(score, 0)

    def test_mate_in_one(self):
        # Scholar's Mate setup: White queen on h5, bishop on c4, Qxf7# is mate
        b = Board("r1bqkb1r/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1")
        best_move, score, stats = self.engine.search(b, max_depth=2)
        self.assertIsNotNone(best_move)
        self.assertEqual(best_move.uci(), "h5f7")

    def test_quiescence_capture_win(self):
        # Hanging queen on e5
        b = Board("4k3/8/8/4q3/4R3/8/8/4K3 w - - 0 1")
        best_move, score, stats = self.engine.search(b, max_depth=2)
        self.assertEqual(best_move.uci(), "e4e5")

    def test_iterative_deepening_returns_valid_move(self):
        b = Board()
        best_move, score, stats = self.engine.search(b, max_depth=3)
        self.assertIsNotNone(best_move)
        self.assertIn(best_move, b.get_legal_moves())


if __name__ == "__main__":
    unittest.main()
