from engine.board import Board

board = Board()

while True:
    print(board)
    print(f"\n{board.turn}'s turn")

    start = input("Select a piece (e.g. e2): ").lower()
    end = input("Move to (e.g. e4): ").lower()

    start_col = ord(start[0]) - ord('a')
    start_row = 8 - int(start[1])

    end_col = ord(end[0]) - ord('a')
    end_row = 8 - int(end[1])

    if board.make_move(start_row, start_col, end_row, end_col):
        print("Move successful!")
    else:
        print("Invalid move! Try again.")