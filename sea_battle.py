import logging
from functions import copy_list
from image_builder import ImageBuilder

from board import Board

INFO = "\033[32m"
WARNING = "\033[33m"
ERROR = "\033[31m"
DEBUG = "\033[34m"
RESET = "\033[0m"

builder = ImageBuilder()


class SeaBattle:
    def __init__(self, bot, players, channels):
        self.bot = bot
        self.players = [
            Player(players[0], channels[0], self),
            Player(players[1], channels[1], self)
        ]

        self.status = "match"
        self.turn = 0

    async def update(self):
        if self.players[0].status == "ready" \
                and self.players[1].status == "ready":
            await self.players[self.turn].turn_request()
        else:
            for player in self.players:
                await player.place_request()

    async def mark_shot(self, player, coords):
        x, y = coords

        if self.players[0].member == player:
            self.players[1].board.board[x][y] = \
                f"*{self.players[1].board.board[x][y]}"
        else:
            self.players[0].board.board[x][y] = \
                f"*{self.players[0].board.board[x][y]}"

        if self.turn == 0:
            self.turn = 1
        else:
            self.turn = 0

    async def get_shots(self, player):
        if self.players[0].member == player:
            board = copy_list(self.players[0].board.board)
        else:
            board = copy_list(self.players[1].board.board)

        for i in range(len(board)):
            for j in range(len(board[i])):
                if str(board[i][j])[0] != "*":
                    board[i][j] = 0

        return board

    async def message(self, message):
        for player in self.players:
            if player.member == message.author:
                await player.process_message(message)


class Player:
    def __init__(self, member, channel, battle):
        self.member = member
        self.channel = channel
        self.battle = battle
        self.status = "preparation"
        self.requested = False

        self.letter_dictionary = {
            "а": 0, "б": 1, "в": 2, "г": 3, "д": 4,
            "е": 5, "ж": 6, "з": 7, "и": 8, "к": 9
        }
        self.digits = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

        self.ship = 1
        self.coords = 0, 0

        self.board = Board()

    def recognize(self, text):
        x, y, rotate = -1, -1, 1

        text = text.split(",")

        for sim in text[0]:
            if self.letter_dictionary.get(sim.lower()) is not None:
                y = self.letter_dictionary[sim.lower()]
            elif sim in self.digits:
                x = int(sim) - 1

                if x == -1:
                    x = 9

        try:
            for sim in text[1]:
                if sim in self.digits:
                    rotate = int(sim)
                    break
        except IndexError:  # если не указан ID поворота, то он равен 1
            pass

        return [x, y, rotate]

    async def place_request(self):
        self.ship = self.board.can_start()

        if self.ship is True:
            if self.status != "ready":
                self.status = "ready"
                await self.channel.send("Вы разместили все корабли. "
                                        "Ждём другого игрока")
                return
            else:
                return
        elif self.requested:
            return

        picture = builder.build_image(self.board.board)

        await self.channel.send("Текущее расположение кораблей", file=picture)
        await self.channel.send(
            f"Пожалуста, выберите клетку, куда хотите поместить {self.ship}"
            f" палубный корабль"
        )
        self.requested = True

    async def input_error(self):
        await self.channel.send(
            'Упс... Ваше сообщение не распознано, пожалуйста, '
            'попробуйте ещё раз'
        )

    async def process_message(self, message):
        text = message.content

        if text.count("выйти") != 0:
            pass

        if self.status == "ready":
            if self.requested:
                x, y, rotate = self.recognize(text)

                if x != -1 and y != -1:
                    await self.battle.mark_shot(
                        self.member,
                        (x, y)
                    )
                else:
                    await self.input_error()
            else:
                await self.input_error()
        else:
            x, y, rotate = self.recognize(text)

            if x == -1 or y == -1 or rotate == -1:
                print(x, y, rotate)
                await self.input_error()
                return
            placed = self.board.place_ship(x, y, rotate, self.ship)

            if not placed:
                await self.input_error()

            self.requested = False

    async def turn_request(self):
        if not self.requested:
            map_shots = await self.battle.get_shots(self.member)

            picture = builder.build_image(map_shots)

            await self.channel.send("Карта выстрелов:", file=picture)
            await self.channel.send("Выберите точку для выстрела")

            self.requested = True
