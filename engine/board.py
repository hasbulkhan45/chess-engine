import numpy as np

from engine.move import Move, square_to_str, str_to_square
from engine.piece import Piece
from engine.zobrist import compute_board_hash
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.queen import Queen
from pieces.rook import Rook


class Board:
    def __init__(self, fen=None):
        self.board = np.full((8, 8), None, dtype=object)
        self.turn = "white"
        self.castling_rights = {"K": True, "Q": True, "k": True, "q": True}
        self.en_passant_target = None  # (row, col) or None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []
        self.position_history = []

        if fen is not None:
            self.load_fen(fen)
        else:
            self.setup()

    def __getitem__(self, item):
        return self.board[item]

    def __setitem__(self, key, value):
        self.board[key] = value

    def setup(self):
        """Sets up the standard initial chess position."""
        self.board.fill(None)
        self.turn = "white"
        self.castling_rights = {"K": True, "Q": True, "k": True, "q": True}
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.move_history = []

        # Pawns
        for i in range(8):
            self.board[1, i] = Pawn("black")
            self.board[6, i] = Pawn("white")

        # Major/minor pieces
        back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i in range(8):
            self.board[0, i] = back_rank[i]("black")
            self.board[7, i] = back_rank[i]("white")

        self.position_history = [compute_board_hash(self)]

    def reset(self):
        """Alias for setup."""
        self.setup()

    def copy(self):
        """Creates an independent copy of the Board."""
        new_board = Board.__new__(Board)
        new_board.board = np.full((8, 8), None, dtype=object)
        for r in range(8):
            for c in range(8):
                p = self.board[r, c]
                if p is not None:
                    new_board.board[r, c] = p.copy()
        new_board.turn = self.turn
        new_board.castling_rights = dict(self.castling_rights)
        new_board.en_passant_target = self.en_passant_target
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        new_board.move_history = list(self.move_history)
        new_board.position_history = list(self.position_history)
        return new_board

    def __str__(self):
        lines = []
        lines.append("  a b c d e f g h")
        lines.append(" +-----------------+")
        for r in range(8):
            row_str = f"{8 - r}| "
            for c in range(8):
                piece = self.board[r, c]
                row_str += f"{str(piece) if piece else '.'} "
            row_str += f"|{8 - r}"
            lines.append(row_str)
        lines.append(" +-----------------+")
        lines.append("  a b c d e f g h")
        return "\n".join(lines)

    def get_king_position(self, color):
        """Returns (row, col) of the King of the specified color."""
        for r in range(8):
            for c in range(8):
                piece = self.board[r, c]
                if isinstance(piece, King) and piece.color == color:
                    return (r, c)
        return None

    def is_square_attacked(self, target_row, target_col, by_color):
        """
        Fast ray-casting check: is (target_row, target_col) attacked by `by_color`?
        Traces outward from the target square for maximum performance.
        """
        # 1. Pawn attacks
        # Opponent pawns attack target if pawn is 1 step back in opponent's advance direction
        pawn_row = target_row + (1 if by_color == "white" else -1)
        if 0 <= pawn_row < 8:
            for dc in (-1, 1):
                pawn_col = target_col + dc
                if 0 <= pawn_col < 8:
                    p = self.board[pawn_row, pawn_col]
                    if isinstance(p, Pawn) and p.color == by_color:
                        return True

        # 2. Knight attacks
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_offsets:
            nr, nc = target_row + dr, target_col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                p = self.board[nr, nc]
                if isinstance(p, Knight) and p.color == by_color:
                    return True

        # 3. King attacks (adjacent squares)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = target_row + dr, target_col + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    p = self.board[nr, nc]
                    if isinstance(p, King) and p.color == by_color:
                        return True

        # 4. Orthogonal sliders (Rook / Queen)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = target_row + dr, target_col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                p = self.board[nr, nc]
                if p is not None:
                    if p.color == by_color and (isinstance(p, (Rook, Queen))):
                        return True
                    break
                nr += dr
                nc += dc

        # 5. Diagonal sliders (Bishop / Queen)
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = target_row + dr, target_col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                p = self.board[nr, nc]
                if p is not None:
                    if p.color == by_color and (isinstance(p, (Bishop, Queen))):
                        return True
                    break
                nr += dr
                nc += dc

        return False

    def is_in_check(self, color):
        """Returns True if the king of `color` is under attack."""
        king_pos = self.get_king_position(color)
        if king_pos is None:
            return False
        opp_color = "black" if color == "white" else "white"
        return self.is_square_attacked(king_pos[0], king_pos[1], opp_color)

    def _get_pseudo_legal_moves(self, color):
        """Generates all pseudo-legal moves for `color` including castling and promotions."""
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r, c]
                if piece is None or piece.color != color:
                    continue

                if isinstance(piece, Pawn):
                    destinations = piece.get_moves(self, r, c)
                    for nr, nc in destinations:
                        # Check promotion
                        promo_rank = 0 if color == "white" else 7
                        is_ep = (self.en_passant_target == (nr, nc) and self.board[nr, nc] is None and c != nc)
                        cap_piece = self.board[r, nc] if is_ep else self.board[nr, nc]

                        if nr == promo_rank:
                            for promo in ("q", "r", "b", "n"):
                                moves.append(Move(
                                    (r, c), (nr, nc), piece_moved=piece,
                                    piece_captured=cap_piece, promotion=promo,
                                    is_castling=False, is_en_passant=False
                                ))
                        else:
                            moves.append(Move(
                                (r, c), (nr, nc), piece_moved=piece,
                                piece_captured=cap_piece, promotion=None,
                                is_castling=False, is_en_passant=is_ep
                            ))

                elif isinstance(piece, King):
                    destinations = piece.get_moves(self, r, c)
                    for nr, nc in destinations:
                        moves.append(Move(
                            (r, c), (nr, nc), piece_moved=piece,
                            piece_captured=self.board[nr, nc], promotion=None,
                            is_castling=False, is_en_passant=False
                        ))

                    # Castling moves
                    moves.extend(self._get_castling_moves(color, r, c, piece))

                else:
                    destinations = piece.get_moves(self, r, c)
                    for nr, nc in destinations:
                        moves.append(Move(
                            (r, c), (nr, nc), piece_moved=piece,
                            piece_captured=self.board[nr, nc], promotion=None,
                            is_castling=False, is_en_passant=False
                        ))
        return moves

    def _get_castling_moves(self, color, r, c, king_piece):
        """Generates legal castling moves for `color`."""
        castling_moves = []
        opp_color = "black" if color == "white" else "white"

        # King must not be currently in check
        if self.is_square_attacked(r, c, opp_color):
            return castling_moves

        if color == "white" and r == 7 and c == 4:
            # White Kingside (O-O)
            if self.castling_rights.get("K") and not king_piece.is_moved:
                rook = self.board[7, 7]
                if isinstance(rook, Rook) and rook.color == "white" and not rook.is_moved:
                    if self.board[7, 5] is None and self.board[7, 6] is None:
                        if (not self.is_square_attacked(7, 5, opp_color) and
                                not self.is_square_attacked(7, 6, opp_color)):
                            castling_moves.append(Move(
                                (7, 4), (7, 6), piece_moved=king_piece,
                                piece_captured=None, promotion=None,
                                is_castling=True, is_en_passant=False
                            ))
            # White Queenside (O-O-O)
            if self.castling_rights.get("Q") and not king_piece.is_moved:
                rook = self.board[7, 0]
                if isinstance(rook, Rook) and rook.color == "white" and not rook.is_moved:
                    if self.board[7, 1] is None and self.board[7, 2] is None and self.board[7, 3] is None:
                        if (not self.is_square_attacked(7, 2, opp_color) and
                                not self.is_square_attacked(7, 3, opp_color)):
                            castling_moves.append(Move(
                                (7, 4), (7, 2), piece_moved=king_piece,
                                piece_captured=None, promotion=None,
                                is_castling=True, is_en_passant=False
                            ))

        elif color == "black" and r == 0 and c == 4:
            # Black Kingside (O-O)
            if self.castling_rights.get("k") and not king_piece.is_moved:
                rook = self.board[0, 7]
                if isinstance(rook, Rook) and rook.color == "black" and not rook.is_moved:
                    if self.board[0, 5] is None and self.board[0, 6] is None:
                        if (not self.is_square_attacked(0, 5, opp_color) and
                                not self.is_square_attacked(0, 6, opp_color)):
                            castling_moves.append(Move(
                                (0, 4), (0, 6), piece_moved=king_piece,
                                piece_captured=None, promotion=None,
                                is_castling=True, is_en_passant=False
                            ))
            # Black Queenside (O-O-O)
            if self.castling_rights.get("q") and not king_piece.is_moved:
                rook = self.board[0, 0]
                if isinstance(rook, Rook) and rook.color == "black" and not rook.is_moved:
                    if self.board[0, 1] is None and self.board[0, 2] is None and self.board[0, 3] is None:
                        if (not self.is_square_attacked(0, 2, opp_color) and
                                not self.is_square_attacked(0, 3, opp_color)):
                            castling_moves.append(Move(
                                (0, 4), (0, 2), piece_moved=king_piece,
                                piece_captured=None, promotion=None,
                                is_castling=True, is_en_passant=False
                            ))

        return castling_moves

    def get_legal_moves(self, color=None):
        """Returns all fully legal moves for `color`."""
        if color is None:
            color = self.turn

        legal_moves = []
        pseudo_moves = self._get_pseudo_legal_moves(color)

        for move in pseudo_moves:
            self._apply_move_direct(move)
            if not self.is_in_check(color):
                legal_moves.append(move)
            self._undo_move_direct()

        return legal_moves

    def get_legal_moves_for_square(self, row, col):
        """Returns all legal moves starting from (row, col)."""
        piece = self.board[row, col]
        if piece is None or piece.color != self.turn:
            return []
        return [m for m in self.get_legal_moves(self.turn) if m.start_row == row and m.start_col == col]

    def _apply_move_direct(self, move):
        """
        Fast internal move application for search/validation.
        Pushes undo state onto self.move_history.
        """
        sr, sc = move.start_row, move.start_col
        er, ec = move.end_row, move.end_col
        piece = self.board[sr, sc]

        # Record undo information
        undo_record = {
            "move": move,
            "piece_moved": piece,
            "piece_is_moved": piece.is_moved,
            "captured_piece": self.board[er, ec],
            "captured_pos": (er, ec),
            "prev_castling_rights": dict(self.castling_rights),
            "prev_en_passant_target": self.en_passant_target,
            "prev_halfmove_clock": self.halfmove_clock,
            "prev_fullmove_number": self.fullmove_number,
            "rook_move": None
        }

        # Handle En Passant
        if move.is_en_passant:
            undo_record["captured_piece"] = self.board[sr, ec]
            undo_record["captured_pos"] = (sr, ec)
            self.board[sr, ec] = None

        # Handle Castling (move the rook)
        if move.is_castling:
            if ec == 6:  # Kingside
                rook_from = (sr, 7)
                rook_to = (sr, 5)
            else:        # Queenside
                rook_from = (sr, 0)
                rook_to = (sr, 3)
            rook = self.board[rook_from]
            undo_record["rook_move"] = (rook_from, rook_to, rook, rook.is_moved if rook else False)
            self.board[rook_to] = rook
            self.board[rook_from] = None
            if rook:
                rook.is_moved = True

        # Move the piece
        self.board[sr, sc] = None
        if move.promotion:
            promo_char = move.promotion.lower()
            piece_classes = {"q": Queen, "r": Rook, "b": Bishop, "n": Knight}
            promo_cls = piece_classes.get(promo_char, Queen)
            promoted_piece = promo_cls(piece.color)
            promoted_piece.is_moved = True
            self.board[er, ec] = promoted_piece
        else:
            self.board[er, ec] = piece
            piece.is_moved = True

        # Update castling rights
        if isinstance(piece, King):
            if piece.color == "white":
                self.castling_rights["K"] = False
                self.castling_rights["Q"] = False
            else:
                self.castling_rights["k"] = False
                self.castling_rights["q"] = False
        elif isinstance(piece, Rook):
            if sr == 7 and sc == 0:
                self.castling_rights["Q"] = False
            elif sr == 7 and sc == 7:
                self.castling_rights["K"] = False
            elif sr == 0 and sc == 0:
                self.castling_rights["q"] = False
            elif sr == 0 and sc == 7:
                self.castling_rights["k"] = False

        # If a rook was captured in a corner
        if undo_record["captured_piece"] is not None and isinstance(undo_record["captured_piece"], Rook):
            if er == 7 and ec == 0:
                self.castling_rights["Q"] = False
            elif er == 7 and ec == 7:
                self.castling_rights["K"] = False
            elif er == 0 and ec == 0:
                self.castling_rights["q"] = False
            elif er == 0 and ec == 7:
                self.castling_rights["k"] = False

        # Update En Passant target
        if isinstance(piece, Pawn) and abs(er - sr) == 2:
            self.en_passant_target = ((sr + er) // 2, sc)
        else:
            self.en_passant_target = None

        # Update clocks
        if isinstance(piece, Pawn) or undo_record["captured_piece"] is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if self.turn == "black":
            self.fullmove_number += 1
            self.turn = "white"
        else:
            self.turn = "black"

        self.move_history.append(undo_record)

    def _undo_move_direct(self):
        """Fast internal move unmaking."""
        if not self.move_history:
            return None

        undo_record = self.move_history.pop()
        move = undo_record["move"]
        sr, sc = move.start_row, move.start_col
        er, ec = move.end_row, move.end_col
        piece = undo_record["piece_moved"]

        # Restore piece at start
        piece.is_moved = undo_record["piece_is_moved"]
        self.board[sr, sc] = piece
        self.board[er, ec] = None

        # Restore captured piece
        if undo_record["captured_piece"] is not None:
            cr, cc = undo_record["captured_pos"]
            self.board[cr, cc] = undo_record["captured_piece"]

        # Restore castling rook
        if undo_record["rook_move"] is not None:
            rook_from, rook_to, rook, rook_was_moved = undo_record["rook_move"]
            self.board[rook_from] = rook
            self.board[rook_to] = None
            if rook:
                rook.is_moved = rook_was_moved

        # Restore state variables
        self.castling_rights = undo_record["prev_castling_rights"]
        self.en_passant_target = undo_record["prev_en_passant_target"]
        self.halfmove_clock = undo_record["prev_halfmove_clock"]
        self.fullmove_number = undo_record["prev_fullmove_number"]
        self.turn = "white" if self.turn == "black" else "black"

        return move

    def make_move(self, start_row, start_col=None, end_row=None, end_col=None, promotion=None):
        """
        Public make_move supporting multiple formats:
        - make_move(start_row, start_col, end_row, end_col, promotion=None)
        - make_move(move_obj)
        - make_move("e2e4") or make_move("e7e8q")
        Returns True if move was legal and executed, False otherwise.
        """
        target_move = None

        # 1. String UCI format (e.g. 'e2e4')
        if isinstance(start_row, str):
            uci_str = start_row.strip().lower()
            try:
                sq1 = str_to_square(uci_str[:2])
                sq2 = str_to_square(uci_str[2:4])
                promo = uci_str[4] if len(uci_str) > 4 else None
            except Exception:
                return False

            legal_moves = self.get_legal_moves(self.turn)
            for m in legal_moves:
                if (m.start_row, m.start_col) == sq1 and (m.end_row, m.end_col) == sq2:
                    if promo is None or m.promotion == promo:
                        target_move = m
                        break

        # 2. Move object
        elif isinstance(start_row, Move):
            m_candidate = start_row
            legal_moves = self.get_legal_moves(self.turn)
            for m in legal_moves:
                if m == m_candidate:
                    target_move = m
                    break

        # 3. Coordinate integers: (sr, sc, er, ec)
        elif start_col is not None and end_row is not None and end_col is not None:
            sr, sc, er, ec = start_row, start_col, end_row, end_col
            legal_moves = self.get_legal_moves(self.turn)
            for m in legal_moves:
                if m.start_row == sr and m.start_col == sc and m.end_row == er and m.end_col == ec:
                    if promotion is None or m.promotion == str(promotion).lower():
                        target_move = m
                        break

        if target_move is None:
            return False

        # Apply move and record position hash
        self._apply_move_direct(target_move)
        self.position_history.append(compute_board_hash(self))
        return True

    def undo_move(self):
        """Public undo_move. Reverts the last move made."""
        if not self.move_history:
            return None
        move = self._undo_move_direct()
        if self.position_history:
            self.position_history.pop()
        return move

    def is_checkmate(self, color=None):
        """Returns True if `color` is in checkmate."""
        if color is None:
            color = self.turn
        return self.is_in_check(color) and len(self.get_legal_moves(color)) == 0

    def checkmate(self, color):
        """Backwards compatibility alias for is_checkmate."""
        return self.is_checkmate(color)

    def is_stalemate(self, color=None):
        """Returns True if `color` is in stalemate (no legal moves, not in check)."""
        if color is None:
            color = self.turn
        return not self.is_in_check(color) and len(self.get_legal_moves(color)) == 0

    def is_fifty_moves(self):
        """Returns True if the 50-move rule applies (100 halfmoves)."""
        return self.halfmove_clock >= 100

    def is_threefold_repetition(self):
        """Returns True if the current position has occurred 3 or more times."""
        if not self.position_history:
            return False
        current_hash = self.position_history[-1]
        return self.position_history.count(current_hash) >= 3

    def is_insufficient_material(self):
        """Returns True if neither side has sufficient material to checkmate."""
        white_pieces = []
        black_pieces = []

        for r in range(8):
            for c in range(8):
                p = self.board[r, c]
                if p is not None:
                    pt = getattr(p, "piece_type", "")
                    if pt in ("p", "r", "q"):
                        return False  # Pawns, rooks, queens can mate
                    if p.color == "white":
                        white_pieces.append((pt, (r + c) % 2))
                    else:
                        black_pieces.append((pt, (r + c) % 2))

        # King vs King
        if len(white_pieces) == 1 and len(black_pieces) == 1:
            return True

        # King + Minor vs King
        if len(white_pieces) == 2 and len(black_pieces) == 1:
            return True
        if len(white_pieces) == 1 and len(black_pieces) == 2:
            return True

        # King + Bishop vs King + Bishop (same color square bishops)
        if len(white_pieces) == 2 and len(black_pieces) == 2:
            w_pt, w_sq_color = [p for p in white_pieces if p[0] != "k"][0]
            b_pt, b_sq_color = [p for p in black_pieces if p[0] != "k"][0]
            if w_pt == "b" and b_pt == "b" and w_sq_color == b_sq_color:
                return True

        return False

    def is_game_over(self):
        """Returns True if the game has ended by checkmate or any draw condition."""
        return (
            self.is_checkmate("white") or
            self.is_checkmate("black") or
            self.is_stalemate("white") or
            self.is_stalemate("black") or
            self.is_fifty_moves() or
            self.is_threefold_repetition() or
            self.is_insufficient_material()
        )

    def get_game_status(self):
        """
        Returns a tuple: (status: str, winner: str or None)
        Status values: 'in_progress', 'checkmate', 'stalemate', 'fifty_moves', 'threefold', 'insufficient_material'
        """
        if self.is_checkmate("white"):
            return ("checkmate", "black")
        if self.is_checkmate("black"):
            return ("checkmate", "white")
        if self.is_stalemate(self.turn):
            return ("stalemate", None)
        if self.is_fifty_moves():
            return ("fifty_moves", None)
        if self.is_threefold_repetition():
            return ("threefold", None)
        if self.is_insufficient_material():
            return ("insufficient_material", None)
        return ("in_progress", None)

    # ------------------ FEN Implementation ------------------
    def get_fen(self):
        """Exports the current position to FEN notation."""
        fen_rows = []
        for r in range(8):
            empty_count = 0
            row_str = ""
            for c in range(8):
                piece = self.board[r, c]
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    pt = getattr(piece, "piece_type", "p")
                    row_str += pt.upper() if piece.color == "white" else pt.lower()
            if empty_count > 0:
                row_str += str(empty_count)
            fen_rows.append(row_str)

        board_part = "/".join(fen_rows)
        turn_part = "w" if self.turn == "white" else "b"

        castling_part = ""
        for flag in ("K", "Q", "k", "q"):
            if self.castling_rights.get(flag):
                castling_part += flag
        if not castling_part:
            castling_part = "-"

        if self.en_passant_target:
            ep_part = square_to_str(self.en_passant_target[0], self.en_passant_target[1])
        else:
            ep_part = "-"

        return f"{board_part} {turn_part} {castling_part} {ep_part} {self.halfmove_clock} {self.fullmove_number}"

    def load_fen(self, fen):
        """Loads a position from a FEN string."""
        parts = fen.strip().split()
        if len(parts) < 4:
            raise ValueError(f"Invalid FEN string: '{fen}'")

        board_part = parts[0]
        turn_part = parts[1]
        castling_part = parts[2]
        ep_part = parts[3]
        halfmove = int(parts[4]) if len(parts) > 4 else 0
        fullmove = int(parts[5]) if len(parts) > 5 else 1

        piece_map = {
            "p": (Pawn, "black"), "P": (Pawn, "white"),
            "n": (Knight, "black"), "N": (Knight, "white"),
            "b": (Bishop, "black"), "B": (Bishop, "white"),
            "r": (Rook, "black"), "R": (Rook, "white"),
            "q": (Queen, "black"), "Q": (Queen, "white"),
            "k": (King, "black"), "K": (King, "white"),
        }

        self.board.fill(None)
        rows = board_part.split("/")
        if len(rows) != 8:
            raise ValueError(f"FEN board must have 8 ranks, got {len(rows)}")

        for r, row_str in enumerate(rows):
            c = 0
            for ch in row_str:
                if ch.isdigit():
                    c += int(ch)
                elif ch in piece_map:
                    cls, color = piece_map[ch]
                    p = cls(color)
                    # For pawns, if not on starting rank, set is_moved = True
                    start_rank = 1 if color == "black" else 6
                    if isinstance(p, Pawn) and r != start_rank:
                        p.is_moved = True
                    self.board[r, c] = p
                    c += 1
                else:
                    raise ValueError(f"Unexpected character '{ch}' in FEN")

        self.turn = "white" if turn_part == "w" else "black"
        self.castling_rights = {
            "K": "K" in castling_part,
            "Q": "Q" in castling_part,
            "k": "k" in castling_part,
            "q": "q" in castling_part,
        }

        if ep_part != "-":
            try:
                self.en_passant_target = str_to_square(ep_part)
            except Exception:
                self.en_passant_target = None
        else:
            self.en_passant_target = None

        self.halfmove_clock = halfmove
        self.fullmove_number = fullmove
        self.move_history = []
        self.position_history = [compute_board_hash(self)]

    @classmethod
    def from_fen(cls, fen):
        """Creates a Board instance directly from a FEN string."""
        return cls(fen=fen)

    # ------------------ SAN Conversion ------------------
    def move_to_san(self, move):
        """Converts a Move into Standard Algebraic Notation (SAN)."""
        if move.is_castling:
            san = "O-O" if move.end_col == 6 else "O-O-O"
        else:
            piece = move.piece_moved
            pt = getattr(piece, "piece_type", "")
            is_capture = (move.piece_captured is not None or move.is_en_passant)

            if pt == "p":
                if is_capture:
                    start_file = chr(ord('a') + move.start_col)
                    san = f"{start_file}x{square_to_str(move.end_row, move.end_col)}"
                else:
                    san = square_to_str(move.end_row, move.end_col)
                if move.promotion:
                    san += f"={move.promotion.upper()}"
            else:
                pt_char = pt.upper()
                # Disambiguation: check if other pieces of same type can reach same destination
                same_type_moves = [
                    m for m in self.get_legal_moves(piece.color)
                    if m != move and getattr(m.piece_moved, "piece_type", "") == pt and
                    (m.end_row, m.end_col) == (move.end_row, move.end_col)
                ]
                disambig = ""
                if same_type_moves:
                    file_diff = any(m.start_col != move.start_col for m in same_type_moves)
                    rank_diff = any(m.start_row != move.start_row for m in same_type_moves)
                    if file_diff:
                        disambig = chr(ord('a') + move.start_col)
                    elif rank_diff:
                        disambig = str(8 - move.start_row)
                    else:
                        disambig = square_to_str(move.start_row, move.start_col)

                cap_str = "x" if is_capture else ""
                dest_str = square_to_str(move.end_row, move.end_col)
                san = f"{pt_char}{disambig}{cap_str}{dest_str}"

        # Check / checkmate suffix
        self._apply_move_direct(move)
        opp_color = self.turn
        if self.is_checkmate(opp_color):
            san += "#"
        elif self.is_in_check(opp_color):
            san += "+"
        self._undo_move_direct()

        return san