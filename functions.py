from discord import Colour, HTTPException, File
import logging

# Настройки цветов логов
INFO = "\033[32m"
WARNING = "\033[33m"
ERROR = "\033[31m"
DEBUG = "\033[34m"
RESET = "\033[0m"

# Цвета для дискорда
GREEN = Colour.green()

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level="DEBUG"
)


def find_role(roles, name_need_role):
    #  поиск роли на сервере
    for role in roles:
        if role.name.lower() == name_need_role.lower():
            return role

    return False


def find_category(categories, name_need_category):
    #  поиск категории на сервере
    for category in categories:
        if category.name.lower() == name_need_category.lower():
            return category

    return False


async def repair_categories(guild, category, text_channels):
    #  исправляет категории с недостаточным количеством каналов
    if "игрок-1" not in text_channels \
            or "игрок-2" not in text_channels:
        logging.warning(
            f"{WARNING}Found a server with a broken category{RESET}"
        )

        if "игрок-1" not in text_channels:
            channel = await guild.create_text_channel(
                name="игрок-1",
                category=category
            )

            await set_default_permissions(guild, channel)
            await set_role_permissions(guild, channel, "Морской Бой Игрок 1")

        if "игрок-2" not in text_channels:
            await guild.create_text_channel(
                name="игрок-2",
                category=category
            )

        logging.info(f"{INFO}Server successfully repaired{RESET}")


async def repair_channel(guild, category_name, channel_names):
    """исправляет каналы без нужной категории или с большим количеством их,
    а также удаляет лишние каналы из этой категории"""
    if find_category(guild.categories, category_name) is False:
        logging.warning(f"{WARNING}Empty channel found{RESET}")

        category = await guild.create_category(
            name=category_name
        )

        for name in channel_names:
            channel = await guild.create_text_channel(
                name=name.lower(),
                category=category
            )

            await set_default_permissions(guild, channel)

            await set_role_permissions(
                guild, channel, f"Морской Бой Игрок {name[-1]}"
            )

        logging.info(f"{INFO}Created new category and channels{RESET}")

    categories = [category.name.lower() for category in guild.categories]

    if categories.count("морской бой") > 1:
        logging.warning(
            f"{WARNING}{guild.name} server with many categories{RESET}"
        )

        reason = "Имеются одинаковые категории"  # причина удаления

        try:
            for category in guild.categories:
                if category.name.lower() == "морской бой":
                    for channel in category.text_channels:
                        await channel.delete(reason=reason)
                        logging.info(
                            f"{INFO}{channel.name} channel was deleted{RESET}"
                        )
                    await category.delete(reason=reason)
                    logging.info(
                        f"{INFO}{category.name} category was deleted{RESET}"
                    )

            await repair_channel(guild, category_name, channel_names)
        except HTTPException:
            logging.warning(
                f'{WARNING}Catch HTTPException in repair_channel func{RESET}'
            )

        logging.info(f'{INFO}Server successfully repaired{RESET}')


async def repair_role(guild):
    roles = [role.name for role in guild.roles]

    if "Морской Бой Игрок 1" not in roles or \
            "Морской Бой Игрок 2" not in roles:
        logging.info(f"{INFO}Found server ({guild.name}) without role{RESET}")

        if "Морской Бой Игрок 1" not in roles:
            await guild.create_role(
                name="Морской Бой Игрок 1",
                colour=GREEN
            )

        if "Морской Бой Игрок 2" not in roles:
            await guild.create_role(
                name="Морской Бой Игрок 2",
                colour=GREEN
            )

        logging.info(f"{INFO}Role successfully created{RESET}")


async def set_default_permissions(guild, channel):
    logging.debug(f"{DEBUG}Setting default permissions{RESET}")
    permissions = channel.overwrites_for(guild.default_role)

    permissions.send_messages = False
    permissions.read_messages = False
    permissions.read_message_history = False

    await channel.set_permissions(guild.default_role, overwrite=permissions)
    logging.debug(f"{DEBUG}Successfully set{RESET}")


async def set_role_permissions(guild, channel, role_name):
    logging.debug(f"{DEBUG}Setting roles permissions{RESET}")

    role = find_role(guild.roles, role_name)

    if role is False:
        await repair_role(guild)
        return set_role_permissions(guild, channel, role_name)

    permissions = channel.overwrites_for(role)

    permissions.send_messages = True
    permissions.read_messages = True
    permissions.read_message_history = True

    await channel.set_permissions(role, overwrite=permissions)
    logging.debug(f"{DEBUG}Successfully set{RESET}")


def copy_list(board):
    tmp_board = []

    for i in board:
        tmp = []
        for j in i:
            tmp.append(j)
        tmp_board.append(tmp)

    return tmp_board

def get_example():
    with open("images/example.png", "rb") as file:
        example = File(file)
        return example
