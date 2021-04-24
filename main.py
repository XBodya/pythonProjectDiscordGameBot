from SeaFight import *
from Mafia import *

TOKEN = "TOKEN"


# Основной класс
class GameBot(SeaBot):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # проверка успешной загрузки
        logging.info(f"{INFO}Bot successfully loaded{RESET}")
        self.update.start()  # запуск циклической активации
        print("SUCCESS LOAD")
        self.clear_lobby.start()
        self.go_cycle.start()

    # Ф-ция для создания лобби
    @commands.command(name='creategame')
    async def create_game_command(self, ctx):
        name = generate_name_lobby()
        logins_lobby[name] = None
        await ctx.send('Создано лобби {}, чтобы подключиться введите "-join {}"'.format(name, name))
        data_lobby[name].append(ctx.author)
        leader_lobby[name] = ctx.author
        status_lobby[name] = False
        change_time[name] = datetime.datetime.now()

    # Ф-ция для входа в лобби
    @commands.command(name='join')
    async def join_to_lobby(self, ctx, name_lobby, *password):
        try:
            if logins_lobby[name_lobby]:
                if password[0] == logins_lobby[name_lobby] \
                        and ctx.author not in data_lobby[name_lobby]:
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

    # Ф-ция для подготовки начала игры
    @commands.command(name='start')
    async def prepare_game(self, ctx, name_lobby):
        if ctx.author == leader_lobby[name_lobby]:
            try:
                roles = []
                for role in ctx.message.guild.roles:
                    if role.name in 'Member':
                        roles.append(role)
                print(roles)
                random.shuffle(roles)
                mafia_role = roles[0]
                police_role = roles[1]
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
                channel_text_all = await ctx.guild.create_text_channel(name_lobby)
                channel_voice_all = await ctx.guild.create_voice_channel(name_lobby, overwrites=None, eason=None)
                channel_mafia = await ctx.guild.create_text_channel(name_lobby + '-mafia',
                                                                    overwrites=overwrites_mafia)
                channel_police = await ctx.guild.create_text_channel(name_lobby + '-police',
                                                                     overwrites=overwrites_police)
                if len(data_lobby[name_lobby]) >= 5:
                    delete_roles[name_lobby] = []
                    cnt_mafia = int(len(data_lobby[name_lobby]) * 0.2) if int(
                        len(data_lobby[name_lobby]) * 0.2) else 1
                    choice_list = data_lobby[name_lobby][:]
                    mafias = []
                    roles_in_lobby[name_lobby] = {}
                    for mafia in range(cnt_mafia):
                        it_mafia = random.choice(choice_list)
                        await it_mafia.add_roles(mafia_role)
                        delete_roles[name_lobby].append((it_mafia, mafia_role))
                        mafias.append(it_mafia)
                        choice_list.remove(it_mafia)
                        roles_in_lobby[name_lobby][it_mafia.name] = 'mafia'
                        await it_mafia.send('В лобби {} вы в составе мафии'.format(name_lobby))
                    don = random.choice(mafias)
                    roles_in_lobby[name_lobby][don.name] = 'don'
                    don_in_lobby[name_lobby] = don.name
                    await don.send('В лобби {} вы дон'.format(name_lobby))
                    used_don_check[don.name] = False
                    police = random.choice(choice_list)
                    roles_in_lobby[name_lobby][police.name] = 'police'
                    await police.send('В лобби {} вы шериф'.format(name_lobby))
                    police_in_lobby[name_lobby] = police.name
                    used_police_check[police.name] = False
                    await police.add_roles(police_role)
                    delete_roles[name_lobby].append((police, police_role))
                    choice_list.remove(police)
                    for member in choice_list[:]:
                        roles_in_lobby[name_lobby][member.name] = 'innocent'
                        await member.send('В лобби {} вы мирный житель'.format(name_lobby))
                    channel_for_lobby[name_lobby] = [channel_text_all, channel_voice_all, channel_mafia,
                                                     channel_police]
                    await self.message_all(ctx, name_lobby, 'Игра в лобби {} начинается'.format(name_lobby))
                    change_time[name_lobby] = datetime.datetime.now()
                    used_votes_in_lobby[name_lobby] = {}
                    for member in data_lobby[name_lobby][:]:
                        used_votes_in_lobby[name_lobby][member.name] = False
                    status_lobby[name_lobby] = False
                    done_lobby[name_lobby] = True
                else:
                    await ctx.send('Ой! В лобби должно быть не менее 5 человек')
            except IndexError:
                await ctx.send('Ой! Ошибка 201')
        else:
            await ctx.send('Ой! Вы не можете начать игру в этом лобби или игра уже идет')

    # Ф-ция для выхода просмотра людей в лобби
    @commands.command(name='view')
    async def view_members(self, ctx, name_lobby):
        try:
            for members in data_lobby[name_lobby]:
                await ctx.send('В лобби {} находятся: {}'.format(name_lobby, members.display_name))
        except Exception:
            await ctx.send('Ой! Похоже такого лобби нету(')

    # Ф-ция для выхода из лобби
    @commands.command(name='quit')
    async def quit_game(self, ctx, name_lobby):
        try:
            data_lobby[name_lobby].remove(ctx.author)
            await ctx.send("Пользователь {} вышел из лобби {}".format(ctx.author, name_lobby))
        except Exception:
            await ctx.send('Ой! Похоже такого лобби нету(')

    # сообщение для всех
    async def message_all(self, ctx, name_lobby, message):
        for i in data_lobby[name_lobby]:
            try:
                await i.send(message)
            except Exception:
                pass

    # Голосование по исключению по деревне
    @commands.command(name='votekick')
    async def vote_kick(self, ctx, name_lobby, candidate):
        try:
            if ctx.author in data_lobby[name_lobby] \
                    and status_lobby[name_lobby] \
                    and not used_votes_in_lobby[ctx.author.name]:
                try:
                    candidate_to_kick[name_lobby][data_lobby[name_lobby][candidate].name] += 1
                    used_votes_in_lobby[
                        ctx.author.name] = True
                    await ctx.author.send("Ваш голос против {} засчитан".format(data_lobby[name_lobby][candidate]))
                except KeyError:
                    candidate_to_kick[name_lobby] = {}
                    candidate_to_kick[name_lobby][data_lobby[name_lobby][candidate].name] = 1
                    used_votes_in_lobby[
                        ctx.author.name] = True
                    await ctx.author.send(
                        "Ваш голос против {} засчитан".format(data_lobby[name_lobby][candidate].name))
        except Exception:
            await ctx.author.send("Ваш голос против {} не засчитан".format(data_lobby[name_lobby][candidate].name))

    # Голосование для убийства
    @commands.command(name='votekill')
    async def vote_kill(self, ctx, name_lobby, candidate):
        try:
            if ctx.channel.split('-')[-1] == 'mafia':
                if ctx.author in data_lobby[name_lobby] \
                        and not status_lobby[name_lobby]:
                    if roles_in_lobby[name_lobby][data_lobby[name_lobby][candidate]] not in {'mafia', 'don'} and \
                            not used_votes_kill_in_lobby[name_lobby][ctx.author.name]:
                        if roles_in_lobby[name_lobby][ctx.author.name] in 'don':
                            don_vote[ctx.author.name] = data_lobby[name_lobby][candidate]
                        else:
                            try:
                                used_votes_kill_in_lobby[name_lobby][ctx.author.name] = True
                                candidate_to_kill[name_lobby][data_lobby[name_lobby][candidate]] += 1
                                await ctx.author.send("Ваш голос на убийство {} засчитан".format(candidate.name))
                            except Exception:
                                used_votes_kill_in_lobby[name_lobby] = {}
                                used_votes_kill_in_lobby[name_lobby][ctx.author.name] = True
                                candidate_to_kill[name_lobby][data_lobby[name_lobby][candidate]] = 1
                                await ctx.author.send("Ваш голос на убийство {} засчитан".format(candidate.name))

        except Exception:
            pass

    # Проверка для Шерифа и Дона
    @commands.command(name='check')
    async def check_member(self, ctx, name_lobby, member):
        try:
            if ctx.channel.split('-')[-1] == 'police':
                if ctx.author in data_lobby[name_lobby] \
                        and not status_lobby[name_lobby] and not used_police_check[ctx.author.name]:
                    try:
                        if police_in_lobby[name_lobby]:
                            checking = roles_in_lobby[name_lobby][data_lobby[name_lobby][member].name]
                            if checking in {'mafia', 'don'}:
                                await ctx.channel.send(
                                    'Выполняю проверку. {} является членом мафии'.format(
                                        data_lobby[name_lobby][member].name))
                            else:
                                await ctx.channel.send(
                                    'Выполняю проверку. {} не является членом мафии'.format(
                                        data_lobby[name_lobby][member].name))
                            used_police_check[ctx.author.name] = True
                    except Exception:
                        pass
            if ctx.channel.split('-')[-1] == 'mafia':
                if ctx.author in data_lobby[name_lobby] \
                        and not status_lobby[name_lobby] and not used_don_check[ctx.author.name]:
                    try:
                        if don_in_lobby[name_lobby]:
                            checking = roles_in_lobby[name_lobby][data_lobby[name_lobby][member].name]
                            if checking in {'innocent', 'police'}:
                                await ctx.channel.send(
                                    'Выполняю проверку. {} является шерифом'.format(
                                        data_lobby[name_lobby][member].name))
                            else:
                                await ctx.channel.send(
                                    'Выполняю проверку. {} не является шерифом'.format(
                                        data_lobby[name_lobby][member].name))
                            used_don_check[ctx.author.name] = True
                    except Exception:
                        pass
        except Exception:
            pass

    # Очистка словарей. Сборщик мусора
    @tasks.loop(minutes=30)
    async def clear_lobby(self):
        for i in data_lobby:
            try:
                if not data_lobby[i]:
                    leader_lobby.pop(i)
                    logins_lobby.pop(i)
                    status_lobby.pop(i)
                    data_lobby.pop(i)
                    channel_for_lobby.pop(i)
            except Exception:
                print("#CLEAR FAILED")
        print('#CLEAR OK')

    # Ф-ция циклически сдвигающая фазы в лобби
    @tasks.loop(seconds=30)
    async def go_cycle(self):
        try:
            for game in change_time:
                try:
                    if done_lobby[game]:
                        if int((str(datetime.datetime.now() - change_time[game]).split(':'))[1]) >= 6:
                            status_lobby[game] ^= True
                            await self.message_all(ctx=None,
                                                   message=(
                                                       'В лобби {} начинается {}'.format(game,
                                                                                         'ночь' if status_lobby[
                                                                                             game] else 'день')),
                                                   name_lobby=game)
                            await self.message_all(ctx=None,
                                                   message=(
                                                       'Напоминаю во время дня можно голосов'
                                                       'ать, а ночью спать или отыгрывать свою роль'),
                                                   name_lobby=game)
                            if status_lobby[game]:
                                used_police_check[police_in_lobby[game]] = False
                                used_don_check[don_in_lobby[game]] = False
                                delete = list()
                                for game_id in candidate_to_kick:
                                    try:
                                        list_candidate = [(candidate_to_kick[game][i], i) for i in
                                                          candidate_to_kick[game]]
                                        result_votes = max(list_candidate)
                                        candidate = None
                                        for candidates in data_lobby[game_id]:
                                            if candidates.name == result_votes[-1]:
                                                candidate = candidates
                                                break
                                        await candidate.send(
                                            'По итогу общего голосования, вас выгоняют из лобби {}'.format(game))
                                        await channel_for_lobby[game][0].send(
                                            'По итогу общего голосования, выгоняют {} из лобби {}'.format(
                                                candidate.name,
                                                game))
                                        for el in used_votes_in_lobby[game_id]:
                                            used_votes_in_lobby[game_id][el] = False
                                        data_lobby[game].remove(candidate)
                                        delete.append(game)
                                    except Exception:
                                        pass
                                for i in delete:
                                    del candidate_to_kick[i]
                            else:
                                delete_kill = list()
                                for game_id in candidate_to_kill:
                                    try:
                                        list_names = list(map(lambda x: x.name, data_lobby[game_id]))
                                        try:
                                            if don_in_lobby[game_id] in list_names \
                                                    and don_vote[don_in_lobby[game_id]]:
                                                await don_vote[don_in_lobby[game_id]].send(
                                                    'Вас, убивают в лобби {}'.format(game_id))
                                                await channel_for_lobby[game][2].send(
                                                    'По инициативе Дона, убивают {} из лобби {}'.format(
                                                        don_vote[don_in_lobby[game_id]].name, game_id))
                                                data_lobby[game].remove(don_vote[don_in_lobby[game_id]])
                                                del don_vote[don_in_lobby[game_id]]
                                            else:
                                                list_candidate = [(candidate_to_kick[game_id][i], i) for i in
                                                                  candidate_to_kick[game_id]]
                                                result_votes = max(list_candidate)
                                                candidate = None
                                                for candidates in data_lobby[game]:
                                                    if candidates.name == result_votes[-1]:
                                                        candidate = candidates
                                                        break
                                                await candidate.send(
                                                    'Вас, убивают в лобби {}'.format(game_id))
                                                await channel_for_lobby[game][2].send(
                                                    'По итогу голосования, убивают {} из лобби {}'.format(
                                                        candidate.name,
                                                        game_id))
                                                for el in used_votes_kill_in_lobby[game_id]:
                                                    used_votes_kill_in_lobby[game_id][el] = False
                                                data_lobby[game].remove(candidate)
                                                delete_kill.append(game_id)
                                        except Exception:
                                            list_candidate = [(candidate_to_kick[game_id][i], i) for i in
                                                              candidate_to_kick[game_id]]
                                            result_votes = max(list_candidate)
                                            candidate = None
                                            for candidates in data_lobby[game]:
                                                if candidates.name == result_votes[-1]:
                                                    candidate = candidates
                                                    break
                                            await candidate.send(
                                                'Вас, убивают в лобби {}'.format(game_id))
                                            await channel_for_lobby[game][2].send(
                                                'По итогу голосования, убивают {} из лобби {}'.format(
                                                    candidate.name,
                                                    game_id))
                                            for el in used_votes_kill_in_lobby[game_id]:
                                                used_votes_kill_in_lobby[game_id][el] = False
                                            data_lobby[game].remove(candidate)
                                            delete_kill.append(game_id)
                                        finally:
                                            pass
                                    except Exception:
                                        pass
                                for i in delete_kill:
                                    del candidate_to_kill[i]
                except Exception:
                    pass

        except IndexError:
            print("NOT FOUND 404")

        except Exception:
            pass

    # Проверка конца игры в лобби
    @tasks.loop(seconds=30)
    async def check_end_game(self):
        delete_lobby = []
        for game in data_lobby:
            try:
                list_mafia = list(filter(lambda x: roles_in_lobby[game][x] in {'mafia', 'don'}, data_lobby[game]))
                cnt_mafia = len(list_mafia)
                if len(data_lobby[game]) - cnt_mafia <= cnt_mafia:
                    await self.message_all(ctx=None,
                                           message=(
                                               'В лобби {} победила мафия'.format(game)),
                                           name_lobby=game)

                delete_lobby.append(game)
            except Exception:
                pass
        for lobby in delete_lobby:
            try:
                data_lobby[lobby].clear()
                for channel in channel_for_lobby[lobby]:
                    await channel.delete()
                for member in delete_roles[lobby]:
                    await member[0].remove_roles(member[1])
            except Exception:
                print("FAILED")


if __name__ == '__main__':
    # Основной запуск
    logging.debug(f'{DEBUG}Loading the bot has started{RESET}')
    bot = commands.Bot(command_prefix='-')
    ds = GameBot(bot)
    bot.add_cog(ds)
    bot.run(TOKEN)
