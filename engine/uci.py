import sys
from engine.board import Board
from engine.search import SearchEngine


class UCIEngine:
    def __init__(self):
        self.board = Board()
        self.searcher = SearchEngine()

    def run(self):
        """Main UCI command processing loop."""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue

                if line == "uci":
                    print("id name Pure Chess Engine")
                    print("id author Hasbul Khan")
                    print("uciok")
                    sys.stdout.flush()

                elif line == "isready":
                    print("readyok")
                    sys.stdout.flush()

                elif line == "ucinewgame":
                    self.board.setup()
                    self.searcher.clear()

                elif line.startswith("position"):
                    self._handle_position(line)

                elif line.startswith("go"):
                    self._handle_go(line)

                elif line == "stop":
                    self.searcher.stopped = True

                elif line == "quit":
                    break

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                # In UCI, suppress raw exceptions to stdout; print info string if needed
                print(f"info string error: {e}")
                sys.stdout.flush()

    def _handle_position(self, line):
        tokens = line.split()
        if len(tokens) < 2:
            return

        moves_idx = -1
        if "moves" in tokens:
            moves_idx = tokens.index("moves")

        pos_type = tokens[1]
        if pos_type == "startpos":
            self.board.setup()
        elif pos_type == "fen":
            fen_tokens = tokens[2:moves_idx] if moves_idx != -1 else tokens[2:]
            fen_str = " ".join(fen_tokens)
            self.board.load_fen(fen_str)

        if moves_idx != -1:
            for uci_move in tokens[moves_idx + 1:]:
                self.board.make_move(uci_move)

    def _handle_go(self, line):
        tokens = line.split()
        depth = 4
        movetime = None

        i = 1
        while i < len(tokens):
            if tokens[i] == "depth" and i + 1 < len(tokens):
                depth = int(tokens[i + 1])
                i += 2
            elif tokens[i] == "movetime" and i + 1 < len(tokens):
                movetime = float(tokens[i + 1]) / 1000.0
                i += 2
            elif tokens[i] in ("wtime", "btime") and i + 1 < len(tokens):
                # Simple time management: divide remaining time by 30
                time_val = float(tokens[i + 1]) / 1000.0
                if (tokens[i] == "wtime" and self.board.turn == "white") or \
                   (tokens[i] == "btime" and self.board.turn == "black"):
                    movetime = max(time_val / 30.0, 0.05)
                i += 2
            else:
                i += 1

        best_move, score, stats = self.searcher.search(self.board, max_depth=depth, time_limit=movetime)

        if best_move is not None:
            print(f"info depth {stats['depth']} score cp {score} nodes {stats['nodes']} nps {stats['nps']}")
            print(f"bestmove {best_move.uci()}")
        else:
            print("bestmove 0000")
        sys.stdout.flush()


if __name__ == "__main__":
    UCIEngine().run()
