import argparse
import sys
import time

from engine.board import Board
from engine.game import Game, GameStatus
from engine.move import square_to_str, str_to_square
from engine.search import SearchEngine
from engine.uci import UCIEngine


def run_perft(board, depth):
    """
    Performance test: counts the total number of leaf nodes at a given depth.
    Used to verify move generator correctness.
    """
    if depth == 0:
        return 1

    moves = board.get_legal_moves(board.turn)
    if depth == 1:
        return len(moves)

    nodes = 0
    for move in moves:
        board._apply_move_direct(move)
        nodes += run_perft(board, depth - 1)
        board._undo_move_direct()
    return nodes


def run_perft_benchmark(depth=4):
    """Runs and benchmarks Perft from starting position."""
    board = Board()
    print(f"\nRunning Perft test up to depth {depth} from starting position...")
    total_start = time.time()

    for d in range(1, depth + 1):
        t0 = time.time()
        nodes = run_perft(board, d)
        dt = max(time.time() - t0, 0.0001)
        nps = int(nodes / dt)
        print(f"Perft({d}): {nodes:,} nodes in {dt:.3f}s ({nps:,} nodes/sec)")

    total_time = time.time() - total_start
    print(f"Completed in {total_time:.3f}s.\n")


def play_vs_ai(user_color="white", depth=4):
    """Interactive game: Human vs Engine in pure CLI."""
    game = Game()
    engine = SearchEngine()

    print(f"\nStarting game vs Engine (AI depth: {depth})")
    print(f"You are playing as {user_color.upper()}.")
    print("Commands: Enter move as 'e2e4' or 'e7e8q'. Type 'undo', 'moves', 'fen', 'pgn', or 'quit'.\n")

    while not game.is_over():
        print(game.board)
        current_turn = game.board.turn

        if game.board.is_in_check(current_turn):
            print(f"\n>>> {current_turn.upper()} is in CHECK! <<<")

        if current_turn == user_color:
            print(f"\nYour turn ({current_turn}):")
            user_input = input("Enter move: ").strip().lower()

            if user_input in ("quit", "exit", "q"):
                print("Game aborted.")
                return
            elif user_input == "undo":
                # Undo both engine's move and user's move
                game.undo_move()
                game.undo_move()
                print("Undid last round of moves.")
                continue
            elif user_input == "fen":
                print("FEN:", game.get_fen())
                continue
            elif user_input == "pgn":
                print("\n" + game.export_pgn())
                continue
            elif user_input.startswith("moves"):
                parts = user_input.split()
                if len(parts) > 1:
                    try:
                        sq = str_to_square(parts[1])
                        sq_moves = game.board.get_legal_moves_for_square(sq[0], sq[1])
                        print(f"Legal moves for {parts[1]}: {[m.uci() for m in sq_moves]}")
                    except Exception as err:
                        print(f"Invalid square: {err}")
                else:
                    print(f"Legal moves: {[m.uci() for m in game.get_legal_moves()]}")
                continue

            success = game.play_move(user_input)
            if not success:
                print("Invalid or illegal move! Try again (e.g. 'e2e4', 'moves', or 'undo').")
                continue
        else:
            print(f"\nEngine ({current_turn}) is thinking...")
            best_move, score, stats = engine.search(game.board, max_depth=depth)
            if best_move is None:
                break
            print(f"Engine played: {best_move.uci()} (eval: {score/100:+.2f}, depth: {stats['depth']}, nodes: {stats['nodes']})")
            game.play_move(best_move)

    # Game Over
    print(game.board)
    print("\n================ GAME OVER ================")
    if game.status == GameStatus.CHECKMATE:
        print(f"Checkmate! Winner: {game.winner.upper()}!")
    elif game.status == GameStatus.STALEMATE:
        print("Draw by Stalemate!")
    elif game.status == GameStatus.DRAW_FIFTY_MOVES:
        print("Draw by 50-move rule!")
    elif game.status == GameStatus.DRAW_THREEFOLD:
        print("Draw by threefold repetition!")
    elif game.status == GameStatus.DRAW_INSUFFICIENT_MATERIAL:
        print("Draw by insufficient material!")

    print("\nFinal PGN:\n")
    print(game.export_pgn())


def play_human_vs_human():
    """Interactive 2-player game on the CLI."""
    game = Game()
    print("\nStarting Human vs Human game.")
    print("Commands: Enter move as 'e2e4'. Type 'undo', 'moves', 'fen', 'pgn', or 'quit'.\n")

    while not game.is_over():
        print(game.board)
        turn = game.board.turn

        if game.board.is_in_check(turn):
            print(f"\n>>> {turn.upper()} is in CHECK! <<<")

        print(f"\n{turn.capitalize()}'s turn")
        user_input = input("Enter move (e.g. e2e4): ").strip().lower()

        if user_input in ("quit", "exit", "q"):
            print("Game exited.")
            return
        elif user_input == "undo":
            undone = game.undo_move()
            if undone:
                print(f"Undid move: {undone.uci()}")
            else:
                print("No moves to undo.")
            continue
        elif user_input == "fen":
            print("FEN:", game.get_fen())
            continue
        elif user_input == "pgn":
            print("\n" + game.export_pgn())
            continue
        elif user_input.startswith("moves"):
            parts = user_input.split()
            if len(parts) > 1:
                try:
                    sq = str_to_square(parts[1])
                    sq_moves = game.board.get_legal_moves_for_square(sq[0], sq[1])
                    print(f"Legal moves for {parts[1]}: {[m.uci() for m in sq_moves]}")
                except Exception as err:
                    print(f"Invalid square: {err}")
            else:
                print(f"Legal moves: {[m.uci() for m in game.get_legal_moves()]}")
            continue

        if not game.play_move(user_input):
            print("Illegal move! Try again.")
        else:
            print("Move successful!\n")

    print(game.board)
    print("\nGame Over:", game.status.value)
    if game.winner:
        print(f"Winner: {game.winner.upper()}")
    print("\n" + game.export_pgn())


def play_ai_vs_ai(depth_white=3, depth_black=3, delay=0.5):
    """Watches two engine instances play against each other."""
    game = Game()
    engine_w = SearchEngine()
    engine_b = SearchEngine()

    print(f"\nStarting Engine vs Engine match (White depth {depth_white}, Black depth {depth_black})")
    move_count = 0

    while not game.is_over() and move_count < 200:
        print(game.board)
        turn = game.board.turn
        engine = engine_w if turn == "white" else engine_b
        depth = depth_white if turn == "white" else depth_black

        best_move, score, stats = engine.search(game.board, max_depth=depth)
        if best_move is None:
            break

        san = game.board.move_to_san(best_move)
        game.play_move(best_move)
        move_count += 1
        print(f"{move_count}. {turn.capitalize()} played: {san} ({best_move.uci()}) [eval: {score/100:+.2f}]")
        time.sleep(delay)

    print(game.board)
    print("\nGame Over:", game.status.value)
    print("\nPGN:\n" + game.export_pgn(white=f"Engine (depth {depth_white})", black=f"Engine (depth {depth_black})"))


def play_classic_twostep():
    """Preserves the original prompt flow from the initial repository."""
    board = Board()
    print("\nRunning in Classic Two-Step input mode.")
    print("Type 'q' at any prompt to exit.\n")

    while not board.is_game_over():
        print(board)
        print(f"\n{board.turn}'s turn")

        start = input("Select a piece (e.g. e2): ").strip().lower()
        if start in ("q", "quit"):
            break
        end = input("Move to (e.g. e4): ").strip().lower()
        if end in ("q", "quit"):
            break

        try:
            start_col = ord(start[0]) - ord('a')
            start_row = 8 - int(start[1])
            end_col = ord(end[0]) - ord('a')
            end_row = 8 - int(end[1])
        except Exception:
            print("Invalid square format! Use format like e2 and e4.")
            continue

        # Check for promotion
        piece = board.board[start_row, start_col]
        promo = None
        if piece and getattr(piece, "piece_type", "") == "p":
            promo_row = 0 if piece.color == "white" else 7
            if end_row == promo_row:
                promo = input("Promote to (q/r/b/n) [default: q]: ").strip().lower() or "q"

        if board.make_move(start_row, start_col, end_row, end_col, promotion=promo):
            print("Move successful!\n")
        else:
            print("Invalid move! Try again.\n")

    print(board)
    status, winner = board.get_game_status()
    print(f"\nGame Over: {status}. Winner: {winner}")


def main():
    parser = argparse.ArgumentParser(description="Pure Chess Engine (CLI & UCI)")
    parser.add_argument("--uci", action="store_true", help="Start UCI protocol mode for chess GUIs")
    parser.add_argument("--perft", type=int, default=None, help="Run Perft move generation test up to specified depth")
    parser.add_argument("--bench", action="store_true", help="Run benchmark suite")
    parser.add_argument("--play", choices=["ai", "human", "ai-vs-ai", "classic"], help="Start a game mode directly")
    parser.add_argument("--depth", type=int, default=4, help="AI search depth (default: 4)")
    parser.add_argument("--color", choices=["white", "black"], default="white", help="Your color when playing vs AI")
    args = parser.parse_args()

    if args.uci:
        UCIEngine().run()
        return

    if args.perft is not None:
        run_perft_benchmark(args.perft)
        return

    if args.bench:
        run_perft_benchmark(4)
        return

    if args.play:
        if args.play == "ai":
            play_vs_ai(user_color=args.color, depth=args.depth)
        elif args.play == "human":
            play_human_vs_human()
        elif args.play == "ai-vs-ai":
            play_ai_vs_ai(depth_white=args.depth, depth_black=args.depth)
        elif args.play == "classic":
            play_classic_twostep()
        return

    # Interactive CLI menu
    print("=" * 44)
    print("           PURE CHESS ENGINE")
    print("=" * 44)
    print(" [1] Play vs Engine (AI)")
    print(" [2] Play Human vs Human")
    print(" [3] Watch AI vs AI match")
    print(" [4] Classic Two-Step Input (Original)")
    print(" [5] Run Perft Move Generator Test")
    print(" [6] Start UCI Protocol Mode")
    print(" [Q] Quit")
    print("=" * 44)

    choice = input("Select an option [1-6, Q]: ").strip().lower()
    if choice == "1":
        color_choice = input("Play as White or Black? [W/b]: ").strip().lower()
        col = "black" if color_choice == "b" else "white"
        try:
            d = int(input("AI Search Depth (default 4): ").strip() or "4")
        except ValueError:
            d = 4
        play_vs_ai(user_color=col, depth=d)
    elif choice == "2":
        play_human_vs_human()
    elif choice == "3":
        play_ai_vs_ai(depth_white=3, depth_black=3)
    elif choice == "4":
        play_classic_twostep()
    elif choice == "5":
        try:
            d = int(input("Depth (default 3): ").strip() or "3")
        except ValueError:
            d = 3
        run_perft_benchmark(d)
    elif choice == "6":
        print("Starting UCI mode... (send UCI commands via stdin)")
        UCIEngine().run()
    else:
        print("Goodbye!")


if __name__ == "__main__":
    main()