import unittest
from engine.board import Board
from engine.move import Move


class TestFenAndSan(unittest.TestCase):
    def test_start_fen(self):
        b = Board()
        expected = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.assertEqual(b.get_fen(), expected)

    def test_fen_roundtrip(self):
        fens = [
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
            "r1bqk2r/pp1p1ppp/2n1pn2/8/1bPN4/2N3P1/PP2PP1P/R1BQKB1R w KQkq - 1 7",
            "8/8/8/4k3/8/8/4K3/8 w - - 0 1",
            "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        ]
        for f in fens:
            b = Board(f)
            self.assertEqual(b.get_fen(), f)

    def test_san_generation(self):
        b = Board()
        # 1. e4
        m1 = Move.from_uci("e2e4", b)
        self.assertEqual(b.move_to_san(m1), "e4")
        b.make_move(m1)

        # 1... e5
        m2 = Move.from_uci("e7e5", b)
        self.assertEqual(b.move_to_san(m2), "e5")
        b.make_move(m2)

        # 2. Nf3
        m3 = Move.from_uci("g1f3", b)
        self.assertEqual(b.move_to_san(m3), "Nf3")
        b.make_move(m3)

    def test_san_check_and_mate(self):
        # Scholar's mate final move SAN should be Qxf7#
        b = Board()
        b.make_move("e2e4")
        b.make_move("e7e5")
        b.make_move("d1h5")
        b.make_move("b8c6")
        b.make_move("f1c4")
        b.make_move("g8f6")
        mate_move = Move.from_uci("h5f7", b)
        self.assertEqual(b.move_to_san(mate_move), "Qxf7#")


if __name__ == "__main__":
    unittest.main()
