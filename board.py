from functions import copy_list


def check_board(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] != 0:
                if i > 0:
                    if board[i - 1][j] != 0 \
                            and board[i - 1][j] != board[i][j]:
                        return False
                    if j > 0:
                        if board[i - 1][j - 1] != 0 \
                                and board[i - 1][j - 1] != board[i][j]:
                            return False
                    if j < len(board[0]) - 1:
                        if board[i - 1][j + 1] != 0 \
                                and board[i - 1][j + 1] != board[i][j]:
                            return False
                if i < len(board) - 1:
                    if board[i + 1][j] != 0 \
                            and board[i + 1][j] != board[i][j]:
                        return False
                    if j > 0:
                        if board[i + 1][j - 1] != 0 \
                                and board[i - 1][j - 1] != board[i][j]:
                            return False
                    if j < len(board[0]) - 1:
                        if board[i + 1][j + 1] != 0 \
                                and board[i - 1][j + 1] != board[i][j]:
                            return False
                if j > 0:
                    if board[i][j - 1] != 0 \
                            and board[i][j - 1] != board[i][j]:
                        return False
                if j < len(board[0]) - 1:
                    if board[i][j + 1] != 0 \
                            and board[i][j + 1] != board[i][j]:
                        return False

    return True


class Board:
    def __init__(self):
        self.board = [[0 for j in range(10)] for i in range(10)]

        self.placed_ships = []
        self.ships = {}

    def place_ship(self, x, y, rotate, count):
        tmp_board = copy_list(self.board)

        if self.board[x][y] != 0:
            return False

        if self.ships.get(str(count)) is None:
            self.ships[str(count)] = 1
        else:
            self.ships[str(count)] += 1

        marker = f"{count}{self.ships[str(count)]}"

        if rotate == 1:
            try:
                for i in range(count):
                    tmp_board[x - i][y] = marker

                    if x - i < 0:
                        raise ValueError
            except Exception:
                return False
        elif rotate == 2:
            try:
                for i in range(count):
                    tmp_board[x][y + i] = marker
            except Exception:
                return False
        elif rotate == 3:
            try:
                for i in range(count):
                    tmp_board[x + i][y] = marker
            except Exception:
                return False
        elif rotate == 4:
            try:
                for i in range(count):
                    tmp_board[x][y - i] = marker

                    if y - i < 0:
                        raise ValueError
            except Exception:
                return False

        if check_board(tmp_board):
            self.board = tmp_board[:]
            self.placed_ships.append(count)

            return True
        return False

    def can_start(self):
        ships = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]

        for ship in self.placed_ships:
            ships.remove(ship)

        if len(ships) != 0:
            return ships[0]

        return True
