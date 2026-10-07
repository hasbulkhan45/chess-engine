from datetime import datetime
from enum import Enum
from engine.board import Board
from engine.move import Move


class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW_FIFTY_MOVES = "draw_fifty_moves"
    DRAW_THREEFOLD = "draw_threefold"
    DRAW_INSUFFICIENT_MATERIAL = "draw_insufficient_material"


class Game:
    def __init__(self, fen=None):
        self.board = Board(fen=fen)
        self.initial_fen = self.board.get_fen()
        self.history = []  # List of dicts: {'move': Move, 'san': str, 'fen': str}
        self.redo_stack = []
        self._update_status()

    def _update_status(self):
        """Updates internal status and winner based on the current board state."""
        raw_status, winner = self.board.get_game_status()
        status_map = {
            "in_progress": GameStatus.IN_PROGRESS,
            "checkmate": GameStatus.CHECKMATE,
            "stalemate": GameStatus.STALEMATE,
            "fifty_moves": GameStatus.DRAW_FIFTY_MOVES,
            "threefold": GameStatus.DRAW_THREEFOLD,
            "insufficient_material": GameStatus.DRAW_INSUFFICIENT_MATERIAL,
        }
        self.status = status_map.get(raw_status, GameStatus.IN_PROGRESS)
        self.winner = winner

    def play_move(self, move_input):
        """
        Executes a move. Accepts Move object, UCI string ('e2e4'), or coordinate tuple.
        Returns True if successful, False if illegal or game already over.
        """
        if self.is_over():
            return False

        # If move_input is string and might be SAN (e.g. 'Nf3' or 'e4')
        move_to_play = None
        legal_moves = self.board.get_legal_moves(self.board.turn)

        if isinstance(move_input, str):
            clean_str = move_input.strip()
            # Try UCI first
            for m in legal_moves:
                if m.uci() == clean_str.lower():
                    move_to_play = m
                    break
            # Try SAN if not matched as UCI
            if move_to_play is None:
                for m in legal_moves:
                    if self.board.move_to_san(m).rstrip("+#") == clean_str.rstrip("+#"):
                        move_to_play = m
                        break
        elif isinstance(move_input, Move):
            for m in legal_moves:
                if m == move_input:
                    move_to_play = m
                    break

        if move_to_play is None:
            # Fall back to board.make_move direct parsing
            success = self.board.make_move(move_input)
            if not success:
                return False
            # Get the move that was just applied from board history
            move_record = self.board.move_history[-1]
            move_to_play = move_record["move"]
            san = self.board.move_to_san(move_to_play) if hasattr(self.board, "move_to_san") else move_to_play.uci()
            self.history.append({
                "move": move_to_play,
                "san": san,
                "fen": self.board.get_fen()
            })
            self.redo_stack.clear()
            self._update_status()
            return True

        # Compute SAN before applying the move
        san = self.board.move_to_san(move_to_play)

        # Apply move
        success = self.board.make_move(move_to_play)
        if not success:
            return False

        self.history.append({
            "move": move_to_play,
            "san": san,
            "fen": self.board.get_fen()
        })
        self.redo_stack.clear()
        self._update_status()
        return True

    def undo_move(self):
        """Undoes the previous move."""
        if not self.history:
            return None
        last_entry = self.history.pop()
        self.board.undo_move()
        self.redo_stack.append(last_entry)
        self._update_status()
        return last_entry["move"]

    def redo_move(self):
        """Redoes the last undone move."""
        if not self.redo_stack:
            return None
        entry = self.redo_stack.pop()
        self.board.make_move(entry["move"])
        self.history.append(entry)
        self._update_status()
        return entry["move"]

    def is_over(self):
        """Returns True if the game is over."""
        return self.status != GameStatus.IN_PROGRESS

    def get_legal_moves(self):
        """Returns all legal moves for current player."""
        return self.board.get_legal_moves(self.board.turn)

    def get_fen(self):
        """Returns current FEN string."""
        return self.board.get_fen()

    def reset(self):
        """Resets the game to the starting position."""
        self.board.setup()
        self.initial_fen = self.board.get_fen()
        self.history.clear()
        self.redo_stack.clear()
        self._update_status()

    def export_pgn(self, event="Casual Game", site="Pure Chess Engine",
                   white="Player 1", black="Player 2"):
        """Exports the game history to standard PGN string format."""
        date_str = datetime.now().strftime("%Y.%m.%d")
        result_str = "*"
        if self.status == GameStatus.CHECKMATE:
            result_str = "1-0" if self.winner == "white" else "0-1"
        elif self.status in (GameStatus.STALEMATE, GameStatus.DRAW_FIFTY_MOVES,
                             GameStatus.DRAW_THREEFOLD, GameStatus.DRAW_INSUFFICIENT_MATERIAL):
            result_str = "1/2-1/2"

        headers = [
            f'[Event "{event}"]',
            f'[Site "{site}"]',
            f'[Date "{date_str}"]',
            f'[Round "1"]',
            f'[White "{white}"]',
            f'[Black "{black}"]',
            f'[Result "{result_str}"]',
        ]

        if self.initial_fen != "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1":
            headers.append('[SetUp "1"]')
            headers.append(f'[FEN "{self.initial_fen}"]')

        # Format move list
        move_tokens = []
        for i, entry in enumerate(self.history):
            if i % 2 == 0:
                move_num = (i // 2) + 1
                move_tokens.append(f"{move_num}. {entry['san']}")
            else:
                move_tokens.append(f"{entry['san']}")

        move_tokens.append(result_str)
        moves_body = " ".join(move_tokens)

        return "\n".join(headers) + "\n\n" + moves_body + "\n"
