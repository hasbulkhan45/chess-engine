# Pure Chess Engine (Python)

A complete, pure Python chess engine built from scratch. Features standard FIDE chess rules, legal move generation, move undo/redo, Forsyth–Edwards Notation (FEN), Standard Algebraic Notation (SAN), Portable Game Notation (PGN) export, positional evaluation, Alpha-Beta minimax search with quiescence search and transposition tables, Universal Chess Interface (UCI) compliance, and a terminal CLI.

> **Pure Engine Focus:** This project contains zero frontend or web UI dependencies. It operates entirely as an engine library, CLI application, and UCI-compatible backend engine for chess GUIs.

---

## Table of Contents

- [Features](#features)
- [Architecture & File Structure](#architecture--file-structure)
- [Requirements & Installation](#requirements--installation)
- [Quick Start](#quick-start)
- [CLI Game Modes & Options](#cli-game-modes--options)
- [UCI Protocol Integration](#uci-protocol-integration)
- [Python API Usage](#python-api-usage)
- [Engine Architecture Deep Dive](#engine-architecture-deep-dive)
  - [Move Generation & Legality](#move-generation--legality)
  - [Evaluation Function](#evaluation-function)
  - [Search & Alpha-Beta Pruning](#search--alpha-beta-pruning)
  - [Zobrist Hashing & Transposition Table](#zobrist-hashing--transposition-table)
- [Testing & Verification](#testing--verification)
  - [Running Unit Tests](#running-unit-tests)
  - [Perft Move Generation Validation](#perft-move-generation-validation)
- [Contributing & License](#license)

---

## Features

### Complete FIDE Chess Rules
- **Piece Movement:** Full movement logic for Pawns, Knights, Bishops, Rooks, Queens, and Kings.
- **Castling:** Kingside ($O-O$) and Queenside ($O-O-O$) with proper checks (cannot castle while in check, through check, or into check; king and rook must not have moved; intervening squares must be empty).
- **En Passant:** Captures and strict 1-ply expiration tracking.
- **Pawn Promotion:** Choice of Queen, Rook, Bishop, or Knight upon reaching the 8th/1st rank.
- **King Safety & Pins:** Fast ray-casting attack detection ensuring illegal moves leaving the king in check are strictly disallowed.
- **Endgame & Draw Conditions:**
  - Checkmate detection
  - Stalemate detection
  - Fifty-Move Rule (100 half-moves without a pawn move or capture)
  - Threefold Repetition (exact board position repetition tracking)
  - Insufficient Material detection ($K$ vs $K$, $K+B$ vs $K$, $K+N$ vs $K$, $K+B$ vs $K+B$ same color)

### Notation & Serialization
- **FEN (Forsyth–Edwards Notation):** Full import (`load_fen`, `from_fen`) and export (`get_fen`).
- **SAN (Standard Algebraic Notation):** Move disambiguation, capture markers, check (`+`), and checkmate (`#`) suffixes (e.g. `e4`, `Nf3`, `exd5`, `Nbd7`, `O-O`, `Qxf7#`).
- **UCI Move Notation:** Standard 4/5 character format (e.g. `e2e4`, `e7e8q`).
- **PGN (Portable Game Notation):** Export complete games with metadata headers and numbered move lists.

### Engine AI & Search
- **Minimax with Alpha-Beta Pruning:** Negamax formulation.
- **Quiescence Search:** Eliminates the horizon effect by searching tactical captures to quiet positions.
- **Transposition Table (TT):** 64-bit Zobrist hashing caching exact, upper bound, and lower bound node evaluations.
- **Move Ordering:**
  - TT best move
  - MVV-LVA (Most Valuable Victim – Least Valuable Attacker) capture ordering
  - Pawn promotions
  - Killer Move Heuristic (two killer moves stored per ply)
  - History Heuristic
- **Iterative Deepening:** Searches depth by depth with time management.
- **Tapered Evaluation:** Blends opening/middle-game and endgame Piece-Square Tables (PST), material count, bishop pair bonus, and pawn structure analysis (doubled/isolated pawns).

### Interfaces
- **Interactive CLI:** Play against the engine, two-player local games, AI vs AI demonstrations, and classic input mode.
- **UCI Protocol:** Full support for `uci`, `isready`, `position`, `go`, `stop`, `ucinewgame`, and `quit`. Connects to external chess GUIs like Arena, Cute Chess, Banksia, or Lichess bots.

---

## Architecture & File Structure

```
chess-engine/
├── engine/
│   ├── __init__.py         # Package entry point exposing Board, Move, Game, etc.
│   ├── board.py            # 8x8 Board representation, move execution, undo, FEN, SAN
│   ├── piece.py            # Base Piece class
│   ├── move.py             # Move representation, UCI conversion, square coordinate helpers
│   ├── game.py             # High-level Game controller, undo/redo stack, PGN export
│   ├── evaluation.py       # Tapered evaluation, Piece-Square Tables (PST), material values
│   ├── search.py           # Minimax, Alpha-Beta, Quiescence search, Move ordering, TT
│   ├── zobrist.py          # 64-bit Zobrist hashing for positions, castling, and en passant
│   └── uci.py              # UCI protocol handler for external chess GUIs
├── pieces/
│   ├── __init__.py         # Pieces package initialization
│   ├── pawn.py             # Pawn movement, double push, en passant
│   ├── knight.py           # Knight jump offsets
│   ├── bishop.py           # Diagonal ray casting
│   ├── rook.py             # Orthogonal ray casting
│   ├── queen.py            # 8-direction ray casting
│   └── king.py             # King 1-step moves
├── tests/
│   ├── __init__.py
│   ├── test_pieces.py      # Individual piece movement tests
│   ├── test_special_moves.py # Castling, en passant, promotion tests
│   ├── test_rules.py       # Checkmate, stalemate, draws, repetition tests
│   ├── test_fen_and_san.py # FEN roundtrip and SAN generation tests
│   ├── test_search.py      # Tactical search, mate-in-1, quiescence tests
│   ├── test_game.py        # Game controller, undo/redo, PGN tests
│   └── test_perft.py       # Perft move generator accuracy tests
├── main.py                 # Pure CLI launcher, game runner, Perft benchmark
├── readme.md               # Project documentation
└── .gitignore              # Ignored files and caches
```

---

## Requirements & Installation

- **Python:** 3.10 or higher
- **Dependencies:** `numpy`

Clone the repository and verify your installation:

```bash
git clone https://github.com/hasbulkhan45/chess-engine.git
cd chess-engine
python3 -m unittest discover tests
```

---

## Quick Start

### 1. Launch the Interactive CLI Menu
```bash
python3 main.py
```
You will be greeted with the engine menu:
```text
============================================
              PURE CHESS ENGINE
============================================
 [1] Play vs Engine (AI)
 [2] Play Human vs Human
 [3] Watch AI vs AI match
 [4] Classic Two-Step Input (Original)
 [5] Run Perft Move Generator Test
 [6] Start UCI Protocol Mode
 [Q] Quit
============================================
```

### 2. Play Directly Against the AI
```bash
# Play as White at depth 4
python3 main.py --play ai --color white --depth 4

# Play as Black at depth 5
python3 main.py --play ai --color black --depth 5
```

### 3. Run UCI Mode (for Chess GUIs)
```bash
python3 main.py --uci
```

### 4. Run Perft Move Generation Benchmark
```bash
python3 main.py --perft 3
```

---

## CLI Game Modes & Options

### Command-Line Arguments

| Flag | Argument | Description |
| :--- | :--- | :--- |
| `--uci` | - | Starts standard UCI protocol mode |
| `--perft` | `<depth>` | Runs Perft move generation test up to specified depth |
| `--bench` | - | Runs standard performance benchmark suite |
| `--play` | `ai \| human \| ai-vs-ai \| classic` | Launches a specific game mode directly |
| `--depth` | `<int>` | Sets AI search depth (default: `4`) |
| `--color` | `white \| black` | Sets your color when playing against AI |

### In-Game CLI Commands

While playing in the CLI, the following commands are available at any prompt:

- `e2e4` or `e7e8q`: Enter moves in standard UCI coordinate format.
- `undo`: Undoes the last move (or both moves when playing against AI).
- `moves`: Prints all currently legal moves for the active side.
- `moves <square>`: Prints legal destination squares for a specific piece (e.g. `moves e2`).
- `fen`: Displays the current position in Forsyth–Edwards Notation.
- `pgn`: Displays the formatted Portable Game Notation move log.
- `quit` or `exit`: Exits the current game session.

---

## UCI Protocol Integration

This engine adheres to the **Universal Chess Interface (UCI)** specification, allowing it to be integrated into third-party chess GUIs (such as **Arena**, **Cute Chess**, **Banksia GUI**, **Scid**, or **Lichess Bot**).

### Connecting to a GUI
1. Open your GUI's engine management settings (e.g., in Arena: *Engines* -> *Install New Engine*).
2. Point the executable to `python3` (or full path to your Python interpreter).
3. Set the arguments to: `/path/to/chess-engine/main.py --uci` (or run `python3 -m engine.uci`).

### Sample UCI Session
```text
uci
id name Pure Chess Engine
id author Hasbul Khan
uciok
isready
readyok
ucinewgame
position startpos moves e2e4 e7e5
go depth 4
info depth 4 score cp 15 nodes 1284 nps 24500
bestmove g1f3
quit
```

---

## Python API Usage

The engine is designed as a modular Python package that can be imported and used in your own scripts.

### Basic Board Manipulation
```python
from engine.board import Board

# Initialize starting position
board = Board()
print(board)

# Make moves (supports UCI string or coordinates)
board.make_move("e2e4")
board.make_move("e7e5")

# Check status
print("Active Turn:", board.turn)
print("Is White in check?", board.is_in_check("white"))
print("Current FEN:", board.get_fen())

# Undo the last move
board.undo_move()
```

### AI Search and Evaluation
```python
from engine.board import Board
from engine.search import SearchEngine
from engine.evaluation import evaluate_board

board = Board("r1bqkb1r/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1")

# Static evaluation (centipawns from White's perspective)
eval_score = evaluate_board(board, perspective="white")
print(f"Static evaluation: {eval_score} cp")

# Search for the best move
engine = SearchEngine()
best_move, score, stats = engine.search(board, max_depth=3)

print(f"Best move found: {best_move.uci()}")  # Outputs: h5f7 (Scholar's Mate!)
print(f"Search stats: {stats}")
```

### Game Management & PGN Export
```python
from engine.game import Game

game = Game()
game.play_move("e2e4")
game.play_move("e7e5")
game.play_move("g1f3")
game.play_move("b8c6")

# Undo / Redo
game.undo_move()
game.redo_move()

# Export complete PGN
pgn_text = game.export_pgn(
    event="World Championship",
    white="Player A",
    black="Player B"
)
print(pgn_text)
```

---

## Engine Architecture Deep Dive

### Move Generation & Legality
- **Ray Casting:** Square attacks are verified by casting rays outward from the target square rather than iterating through every enemy piece. This reduces check detection time by over 80%.
- **O(1) Make / Undo Stack:** Moves are applied in-place to the board matrix. Undo information (captured piece, previous castling rights, previous en passant target, halfmove clock) is pushed to a lightweight history stack, allowing instant reversion without array copies.

### Evaluation Function
The engine utilizes a **tapered evaluation** that smoothly interpolates between middle-game and end-game phases:
- **Material Weights:** Pawn: `100`, Knight: `320`, Bishop: `330`, Rook: `500`, Queen: `900`, King: `20000`.
- **Piece-Square Tables (PST):** Position-specific rewards and penalties for every square on the board for both middle-game and endgame (e.g., central knight outposts, rooks on 7th rank, king shelter in midgame vs. king centralization in endgame).
- **Positional Factors:**
  - Bishop pair bonus (+35 cp)
  - Doubled pawns penalty (-20 cp)
  - Isolated pawns penalty (-15 cp)

### Search & Alpha-Beta Pruning
- **Negamax Framework:** Simplifies tree search by maximizing $-score$ recursively for the side to move.
- **Quiescence Search:** At depth 0, non-quiet positions continue evaluating captures ordered by MVV-LVA until a stable position is reached, eliminating catastrophic miscalculations due to horizon effects.
- **Move Ordering Pipeline:**
  1. Transposition table best move
  2. Winning/equal captures sorted by MVV-LVA
  3. Pawn promotions
  4. Killer moves (moves causing cutoffs at the current ply)
  5. History heuristic
  6. Quiet moves

### Zobrist Hashing & Transposition Table
- Each board state maps to a unique 64-bit integer using pseudorandom Zobrist bitstrings for piece positions, active turn, castling rights, and en passant files.
- The Transposition Table caches entries with depth, cutoff flag (`EXACT`, `LOWERBOUND`, `UPPERBOUND`), evaluation score, and best move, avoiding redundant subtree exploration across iterative deepening iterations.

---

## Testing & Verification

### Running Unit Tests

The test suite covers piece movement, special rules, checkmate/stalemate detection, FEN serialization, SAN notation, and tactical AI search:

```bash
python3 -m unittest discover -v tests
```

### Perft Move Generation Validation

**Perft (Performance Test)** counts the total number of leaf nodes at a given depth. It is the gold standard for validating the correctness of a chess engine's move generator.

```bash
python3 main.py --perft 3
```

#### Starting Position Benchmark Results

| Depth | Expected Nodes | Actual Engine Nodes | Result |
| :---: | :---: | :---: | :---: |
| **1** | 20 | 20 | Pass |
| **2** | 400 | 400 | Pass |
| **3** | 8,902 | 8,902 | Pass |

#### Kiwipete Position Benchmark Results
*Position:* `r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1`

| Depth | Expected Nodes | Actual Engine Nodes | Result |
| :---: | :---: | :---: | :---: |
| **1** | 48 | 48 | Pass |
| **2** | 2,039 | 2,039 | Pass |

---

## License

This project is licensed under the MIT License. Feel free to use, modify, and build upon it for research, study, or competitive play.
