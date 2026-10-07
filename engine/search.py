import time
from engine.evaluation import evaluate_board, PIECE_VALUES
from engine.zobrist import compute_board_hash

FLAG_EXACT = 0
FLAG_LOWERBOUND = 1
FLAG_UPPERBOUND = 2

MATE_SCORE = 100000


def get_mvv_lva_score(move):
    """Calculates Most Valuable Victim - Least Valuable Attacker score for move ordering."""
    if move.piece_captured is None and not move.is_en_passant:
        return 0
    victim_val = 100 if move.is_en_passant else PIECE_VALUES.get(getattr(move.piece_captured, "piece_type", "p"), 100)
    attacker_val = PIECE_VALUES.get(getattr(move.piece_moved, "piece_type", "p"), 100)
    return 10 * victim_val - attacker_val


class SearchEngine:
    def __init__(self):
        self.tt = {}  # Transposition table: hash -> (depth, flag, score, best_move)
        self.killer_moves = {}  # ply -> [move1, move2]
        self.history = {}  # (start_sq, end_sq) -> score
        self.nodes_visited = 0
        self.start_time = 0
        self.time_limit = None
        self.stopped = False

    def clear(self):
        """Clears the transposition table and search heuristics."""
        self.tt.clear()
        self.killer_moves.clear()
        self.history.clear()

    def order_moves(self, board, moves, tt_move=None, ply=0):
        """Scores and orders moves for optimal alpha-beta pruning."""
        def score_move(move):
            # 1. Transposition table move
            if tt_move is not None and move == tt_move:
                return 1000000

            # 2. Captures by MVV-LVA
            if move.piece_captured is not None or move.is_en_passant:
                return 100000 + get_mvv_lva_score(move)

            # 3. Promotions
            if move.promotion:
                promo_prio = {"q": 90000, "r": 80000, "b": 70000, "n": 60000}
                return promo_prio.get(move.promotion, 50000)

            # 4. Killer moves
            killers = self.killer_moves.get(ply, [])
            if len(killers) > 0 and move == killers[0]:
                return 9000
            if len(killers) > 1 and move == killers[1]:
                return 8000

            # 5. History heuristic
            return self.history.get((move.start_square, move.end_square), 0)

        return sorted(moves, key=score_move, reverse=True)

    def is_time_up(self):
        """Checks whether the allocated search time limit has been exceeded."""
        if self.stopped:
            return True
        if self.time_limit is not None and (time.time() - self.start_time) >= self.time_limit:
            self.stopped = True
            return True
        return False

    def quiescence(self, board, alpha, beta, ply=0, max_q_depth=6):
        """
        Quiescence search: evaluates captures until a tactically quiet position is reached.
        Prevents the horizon effect.
        """
        self.nodes_visited += 1

        if self.is_time_up():
            return alpha

        stand_pat = evaluate_board(board, perspective="turn")

        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        if ply >= max_q_depth:
            return stand_pat

        # Generate captures only
        legal_moves = board.get_legal_moves(board.turn)
        captures = [m for m in legal_moves if m.piece_captured is not None or m.is_en_passant or m.promotion]

        ordered_captures = sorted(captures, key=get_mvv_lva_score, reverse=True)

        for move in ordered_captures:
            board._apply_move_direct(move)
            score = -self.quiescence(board, -beta, -alpha, ply + 1, max_q_depth)
            board._undo_move_direct()

            if self.stopped:
                return alpha

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def negamax(self, board, depth, alpha, beta, ply=0):
        """Negamax search with Alpha-Beta pruning, TT lookup, and move ordering."""
        self.nodes_visited += 1

        if self.is_time_up():
            return 0, None

        # Check for repetition or 50-move rule
        if ply > 0 and (board.is_threefold_repetition() or board.is_fifty_moves() or board.is_insufficient_material()):
            return 0, None

        pos_hash = compute_board_hash(board)
        tt_entry = self.tt.get(pos_hash)
        tt_move = None

        if tt_entry is not None:
            tt_depth, tt_flag, tt_score, tt_best = tt_entry
            tt_move = tt_best
            if tt_depth >= depth and ply > 0:
                if tt_flag == FLAG_EXACT:
                    return tt_score, tt_best
                elif tt_flag == FLAG_LOWERBOUND and tt_score > alpha:
                    alpha = tt_score
                elif tt_flag == FLAG_UPPERBOUND and tt_score < beta:
                    beta = tt_score
                if alpha >= beta:
                    return tt_score, tt_best

        # Leaf node -> run quiescence search
        if depth <= 0:
            q_score = self.quiescence(board, alpha, beta, ply)
            return q_score, None

        legal_moves = board.get_legal_moves(board.turn)

        # Terminal conditions: checkmate or stalemate
        if not legal_moves:
            if board.is_in_check(board.turn):
                return -MATE_SCORE + ply, None
            return 0, None  # Stalemate

        ordered_moves = self.order_moves(board, legal_moves, tt_move=tt_move, ply=ply)
        best_move = ordered_moves[0]
        best_score = -float("inf")
        original_alpha = alpha

        for move in ordered_moves:
            board._apply_move_direct(move)
            score, _ = self.negamax(board, depth - 1, -beta, -alpha, ply + 1)
            score = -score
            board._undo_move_direct()

            if self.stopped:
                return best_score if best_score != -float("inf") else 0, best_move

            if score > best_score:
                best_score = score
                best_move = move

            if score > alpha:
                alpha = score

            if alpha >= beta:
                # Beta cutoff - update heuristics
                if move.piece_captured is None and not move.is_en_passant:
                    # Update killer moves
                    killers = self.killer_moves.setdefault(ply, [])
                    if move not in killers:
                        killers.insert(0, move)
                        if len(killers) > 2:
                            killers.pop()
                    # Update history
                    sq_key = (move.start_square, move.end_square)
                    self.history[sq_key] = self.history.get(sq_key, 0) + depth * depth
                break

        # Record in Transposition Table
        if not self.stopped:
            if best_score <= original_alpha:
                flag = FLAG_UPPERBOUND
            elif best_score >= beta:
                flag = FLAG_LOWERBOUND
            else:
                flag = FLAG_EXACT
            self.tt[pos_hash] = (depth, flag, best_score, best_move)

        return best_score, best_move

    def search(self, board, max_depth=4, time_limit=None):
        """
        Iterative deepening search.
        Returns: (best_move, best_score, stats_dict)
        """
        self.nodes_visited = 0
        self.start_time = time.time()
        self.time_limit = time_limit
        self.stopped = False

        legal_moves = board.get_legal_moves(board.turn)
        if not legal_moves:
            return None, 0, {"depth": 0, "nodes": 0, "time": 0, "nps": 0}

        best_move = legal_moves[0]
        best_score = 0
        depth_reached = 0

        for depth in range(1, max_depth + 1):
            score, move = self.negamax(board, depth, -float("inf"), float("inf"), ply=0)

            if self.stopped and depth > 1:
                break

            if move is not None:
                best_move = move
                best_score = score
            depth_reached = depth

            # If checkmate is found, can terminate search early
            if abs(best_score) >= MATE_SCORE - 100:
                break

            if self.is_time_up():
                break

        elapsed = max(time.time() - self.start_time, 0.0001)
        nps = int(self.nodes_visited / elapsed)

        stats = {
            "depth": depth_reached,
            "nodes": self.nodes_visited,
            "score": best_score,
            "time": elapsed,
            "nps": nps
        }

        return best_move, best_score, stats
