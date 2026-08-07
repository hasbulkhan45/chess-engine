from engine.board import Board
def chess_to_index(move):
    files = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7
    }

    col = files[move[0].lower()]
    row = 8 - int(move[1])

    return row, col


board = Board()

while True:
    print(board)
    print(f"\n{board.turn}'s turn")

    start = input("Move from (e.g. e2): ")
    end = input("Move to (e.g. e4): ")

    start_row, start_col = chess_to_index(start)
    end_row, end_col = chess_to_index(end)

    if board.make_move(start_row, start_col, end_row, end_col):
        print("Move successful!")
    else:
        print("Invalid move! Try again.")