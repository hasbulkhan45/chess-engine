import unittest
from engine.board import Board
from main import run_perft


class TestPerft(unittest.TestCase):
    def test_perft_startpos(self):
        b = Board()
        self.assertEqual(run_perft(b, 1), 20)
        self.assertEqual(run_perft(b, 2), 400)
        self.assertEqual(run_perft(b, 3), 8902)

    def test_perft_kiwipete(self):
        # Kiwipete is the ultimate chess engine test position for edge cases
        kiwipete_fen = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
        b = Board(kiwipete_fen)
        self.assertEqual(run_perft(b, 1), 48)
        self.assertEqual(run_perft(b, 2), 2039)


if __name__ == "__main__":
    unittest.main()
