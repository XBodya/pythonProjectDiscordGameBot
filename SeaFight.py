from discord.ext import commands, tasks
from config import settings
from discord import HTTPException, Colour
from game_finder import GameFinder
from functions import repair_role, repair_channel, repair_categories
from functions import find_category
import logging

# Настройки цветов логов
INFO = "\033[32m"
WARNING = "\033[33m"
ERROR = "\033[31m"
DEBUG = "\033[34m"
RESET = "\033[0m"

# Цвета для дискорда
GREEN = Colour.green()


class SeaBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.game = GameFinder(self.client)

        self.command_list = {
            "help_me": "Выводит список всех команд"
        }

        self.sea_commands = {
            "find": ["поиск", "найти", "gjbcr", "yfqnb", "играть"]
        }

    @tasks.loop(seconds=3)  # циклическая активация метода каждые 3 секунды
    async def update(self):
        #  обновление всех серверов и поиск серверов без нужных каналов
        for guild in self.client.guilds:
            await repair_role(guild)
            await repair_channel(guild, "Морской бой", ["игрок-1", "игрок-2"])

            category = find_category(guild.categories, "Морской бой")
            text_channels = [channel.name.lower() for channel in
                             category.text_channels]

            await repair_categories(guild, category, text_channels)
            await self.game.find_channels(guild)

        await self.game.match_update()

    @commands.Cog.listener()
    async def on_ready(self):
        # проверка успешной загрузки
        logging.info(f"{INFO}Bot successfully loaded{RESET}")

        self.update.start()  # запуск циклической активации

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.name.lower() == "игрок-1" \
                or message.channel.name.lower() == "игрок-2":
            await self.game.matches[message.guild.id].message(message)

    @commands.command()
    async def help_me(self, context):
        # вывод списка команд и краткого пояснения
        logging.debug(f"{DEBUG}Help request{RESET}")

        message = ""

        for key in self.command_list:
            message += f"{key} - {self.command_list[key]}\n"

        await context.send(message)

        logging.info(f"{INFO}Send answer for help request{RESET}")

    @commands.command(name="морской_бой")
    async def sea_battle(self, context, action=None):
        if action.lower() in self.sea_commands["find"]:
            await self.game.find_game(
                context.guild,
                context.author,
                context)


if __name__ == '__main__':
    logging.debug(f'{DEBUG}Loading the bot has started{RESET}')

    bot = commands.Bot(command_prefix='-')
    ds = SeaBot(bot)
    bot.add_cog(ds)

    bot.run("TOKEN")
