import random
from discord.ext import commands
import discord
import time
import schedule
import datetime

# name_lobby: [name_member, ...]
data_lobby = {}
# name_lobby: password_lobby
logins_lobby = {}
# name_lobby: leader_lobby
leader_lobby = {}
# name_lobby: lobby_status
status_lobby = {}
# name_lobby: lobby_votes
votes_in_lobby = {}
roles_in_lobby = {}
police_in_lobby = {}
used_mafia_in_lobby = {}
TOKEN = "ODI5MDQ0ODQ0MTc2NjA1MjE1.YGyaLQ.lC9fu8DYToAxQVexdpBmEKPLhDk"
game_bot = commands.Bot(command_prefix='-')


def generate_name_lobby():
    name = str(random.randint(1, 1000000))
    while name in data_lobby:
        name = str(random.randint(1, 1000000))
    data_lobby[name] = []
    return name


def clear_lobby():
    for i in data_lobby:
        try:
            if not data_lobby[i]:
                leader_lobby.pop(i)
                logins_lobby.pop(i)
                status_lobby.pop(i)
                data_lobby.pop(i)
        except Exception:
            print("#CLEAR FAILED")
    print('#CLEAR OK')


def generate_password():
    chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return ''.join([random.choice(chars) for i in range(6)])


class GameBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='creategame')
    async def create_game_command(self, ctx, *password):
        name = generate_name_lobby()
        if password == 'password=True':
            if password[0] == 'password=True':
                cur_password = generate_password()
                logins_lobby[name] = cur_password
                data_lobby[name].append(ctx.author)
                await ctx.send(
                    'Создано приватное лобби {}, '
                    'чтобы подключиться введите "-join {} "пароль от лобби" "'.format(name, name))
                await ctx.author.send('Создано приватное лобби: {}, пароль от лобби: {}'.format(name, cur_password))
        else:
            logins_lobby[name] = None
            await ctx.send('Создано лобби {}, чтобы подключиться введите "-join {}"'.format(name, name))
            data_lobby[name].append(ctx.author)
        leader_lobby[name] = ctx.author
        status_lobby[name] = False

    @commands.command(name='join')
    async def join_to_lobby(self, ctx, name_lobby, *password):
        try:
            if logins_lobby[name_lobby]:
                if password[0] == logins_lobby[name_lobby] and ctx.author not in data_lobby[name_lobby]:
                    data_lobby[name_lobby].append(ctx.author)
                    await ctx.send('Пользователь {} подключился к лобби {}'.format(ctx.author, name_lobby))
                else:
                    ctx.send('Ой! Похоже пароль от лобби неверный или вы уже находитесь в лобби.')
            else:
                if ctx.author not in data_lobby[name_lobby]:
                    data_lobby[name_lobby].append(ctx.author)
                    await ctx.send('Пользователь {} подключился к лобби {}'.format(ctx.author, name_lobby))
                else:
                    await ctx.send('Ой! Вы уже находитесь в лобби.')
        except Exception:
            await ctx.send('Ой! Похоже такого лобби нету(')

    @commands.command(name='start')
    async def start_game(self, ctx, name_lobby):
        if ctx.author == leader_lobby[name_lobby]:
            try:
                roles = []
                for role in ctx.message.guild.roles:
                    if role.name == 'Member':
                        roles.append(role)
                random.shuffle(roles)
                not_mafia_role = roles[0]
                mafia_role = roles[1]
                police_role = roles[2]
                overwrites_mafia = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                    mafia_role: discord.PermissionOverwrite(read_messages=True)
                }
                overwrites_police = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                    police_role: discord.PermissionOverwrite(read_messages=True)
                }
                channel_all = await ctx.guild.create_text_channel(name_lobby)
                channel_mafia = await ctx.guild.create_text_channel(name_lobby + '-mafia',
                                                                    overwrites=overwrites_mafia)
                channel_police = await ctx.guild.create_text_channel(name_lobby + '-police',
                                                                     overwrites=overwrites_police)
                # time.sleep(4)
                # await channel.delete()
                if len(data_lobby[name_lobby]) >= 5:
                    cnt_mafia = int(len(data_lobby[name_lobby]) * 0.2) if int(len(data_lobby[name_lobby]) * 0.2) else 1
                    choice_list = data_lobby[name_lobby][:]
                    mafias = []
                    for mafia in range(cnt_mafia):
                        it_mafia = random.choice(choice_list)
                        await it_mafia.add_roles(mafia_role)
                        mafias.append(it_mafia)
                        choice_list.remove(it_mafia)
                        roles_in_lobby[name_lobby][it_mafia.name] = 'mafia'
                    roles_in_lobby[name_lobby][random.choice(mafias).name] = 'don'
                    police = random.choice(choice_list)
                    police_in_lobby[name_lobby] = police
                    await police.get_roles(police_role)
                    choice_list.remove(police)
                    innocents = choice_list[:]
                    await self.message_all(ctx, name_lobby, 'Игра в лобби {} начинается'.format(name_lobby))
                    while len(data_lobby[name_lobby]) and mafias and len(data_lobby[name_lobby]) - len(mafias) > len(
                            mafias):
                        await self.message_all(ctx,
                                               name_lobby,
                                               'Начинается день, у вас есть {} минут для обсуждений и голосования'.format(
                                                   len(data_lobby[name_lobby]) + 2))
                        status_lobby[name_lobby] = True
                        votes_in_lobby[name_lobby] = []
                        start = datetime.datetime.now()
                        time.sleep(1)
                        while int(str(datetime.datetime.now() - start).split(':')[1]) < (
                                len(data_lobby[name_lobby]) + 2):
                            pass
                        try:
                            candidates = []
                            for key, item in votes_in_lobby[name_lobby].items():
                                candidates.append((item, key))
                            left = max(candidates)
                            await left[-1].send("Вас изгоняют по итогу общего голосования")
                            data_lobby[name_lobby].remove(left[-1])
                        except Exception:
                            pass
                        await self.message_all(ctx, name_lobby,
                                               'Начинается ночь через {} минут наступит день'.format(
                                                   len(data_lobby[name_lobby])))
                        start = datetime.datetime.now()
                        time.sleep(1)
                        while int(str(datetime.datetime.now() - start).split(':')[1]) < (
                                len(data_lobby[name_lobby])):
                            pass
                    else:
                        await ctx.send('Ой! В лобби должно быть не менее 5 человек')
            except IndexError:
                await ctx.send('Ой! Ошибка 201')

            except Exception:
                await ctx.send('Неизвестная ошибка(')
        else:
            await ctx.send('Ой! Вы не можете начать игру в этом лобби или игра уже идет')

    @commands.command(name='view')
    async def view_members(self, ctx, name_lobby):
        try:
            await ctx.send('В лобби {} находятся: {}'.format(name_lobby, data_lobby[name_lobby][0].display_name))
        except Exception:
            await ctx.send('Ой! Похоже такого лобби нету(')

    @commands.command(name='quit')
    async def view_members(self, ctx, name_lobby):
        try:
            data_lobby[name_lobby].remove(ctx.author)
            await ctx.send("Пользователь {} вышел из лобби {}".format(ctx.lobby, name_lobby))
        except Exception:
            await ctx.send('Ой! Похоже такого лобби нету(')

    async def message_all(self, ctx, name_lobby, message):
        for i in data_lobby[name_lobby]:
            await i.send(message)

    @commands.command(name='votekick')
    async def vote_kick(self, ctx, name_lobby, candidate):
        try:
            if ctx.author in data_lobby[name_lobby] \
                    and status_lobby[name_lobby] and candidate in data_lobby[name_lobby]:
                try:
                    votes_in_lobby[name_lobby] += 1
                    await ctx.author.send("Ваш голос против {} засчитан".format(candidate.name))
                except KeyError:
                    votes_in_lobby[name_lobby] = 1
                    await ctx.author.send("Ваш голос против {} засчитан".format(candidate.name))
        except Exception:
            await ctx.author.send("Ваш голос против {} не засчитан".format(candidate.name))

    @commands.command(name='votekill')
    async def vote_kill(self, ctx, name_lobby, candidate):
        try:
            if ctx.channel.split('-')[-1] == 'mafia':
                if ctx.author in data_lobby[name_lobby] and not status_lobby[name_lobby] and candidate in data_lobby[
                    name_lobby] \
                        and candidate in roles_in_lobby[name_lobby]:
                    if roles_in_lobby[name_lobby][candidate] != 'mafia':
                        candidate.send("Ой вас убила мафия, к сожалению вы выходите из игры")
                        data_lobby[name_lobby].remove(candidate)
        except Exception:
            pass

    @commands.command(name='test')
    async def test(self, ctx):
        def job():
            print('work')

        schedule.every(6).seconds.do(job)

    @commands.command(name='test1')
    async def test2(self, ctx):
        print("OK")


if __name__ == '__main__':
    game_bot.add_cog(GameBot(game_bot))
    game_bot.run(TOKEN)
    schedule.every(30).minutes.do(clear_lobby)
    while True:
        schedule.run_pending()
