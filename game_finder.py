import logging
from functions import find_category, find_role, get_example
from sea_battle import SeaBattle
from discord import File

INFO = "\033[32m"
WARNING = "\033[33m"
ERROR = "\033[31m"
DEBUG = "\033[34m"
RESET = "\033[0m"


class GameFinder:
    def __init__(self, bot):
        self.discord_bot = bot

        self.channels = dict()
        self.ready_players = dict()
        self.matches = dict()

    async def find_game(self, guild, player, context):
        #  ждём пока собирутся два игрока для начала игры
        logging.debug(f"{DEBUG}Find game request{RESET}")

        if self.ready_players.get(guild.id) is None:
            self.ready_players[guild.id] = [player]
            await context.send("Ожидаю второго игрока...")

            logging.debug(f"{DEBUG}Record player{RESET}")
        elif len(self.ready_players[guild.id]) == 1:
            if self.ready_players[guild.id][0] != player:
                self.ready_players[guild.id].append(player)
                logging.debug(f"{DEBUG}Starting game{RESET}")

                await self.start_game(guild)
                for channel in self.channels[guild.id]:
                    await channel.send(
                        "Примеры ID поворота корабля. Пишите координаты "
                        "клетки и ID поворота через ';'. Например, 'А0 , 2'",
                        file=get_example()
                    )

    async def start_game(self, guild):
        #  выдаём игрокам роли и начинаем игру
        player_1 = self.ready_players[guild.id][0]
        player_2 = self.ready_players[guild.id][1]

        role_1 = find_role(guild.roles, "морской бой игрок 1")
        role_2 = find_role(guild.roles, "морской бой игрок 2")

        if role_1 is False or role_2 is False:
            logging.error(f"{ERROR}Role not found{RESET}")
            self.ready_players[guild.id] = None
            return

        await player_1.add_roles(role_1)
        await player_2.add_roles(role_2)

        self.matches[guild.id] = SeaBattle(
            self.discord_bot,
            self.ready_players[guild.id],
            self.channels[guild.id]
        )

    async def find_channels(self, guild):
        #  ищем каналы для игры
        category = find_category(guild.categories, "морской бой")

        if category is False:
            return
        elif self.channels.get(guild.id) is not None:
            return

        for channel in category.channels:
            if channel.name.lower() == "игрок-1":
                if self.channels.get(guild.id) is None:
                    self.channels[guild.id] = [channel]
                elif len(self.channels[guild.id]) != 2:
                    self.channels[guild.id].append(channel)
            elif channel.name.lower() == "игрок-2":
                if self.channels.get(guild.id) is None:
                    self.channels[guild.id] = [channel]
                elif len(self.channels[guild.id]) != 2:
                    self.channels[guild.id].append(channel)

    async def match_update(self):
        for match in self.matches:
            await self.matches[match].update()
