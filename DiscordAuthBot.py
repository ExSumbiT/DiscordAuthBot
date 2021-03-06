import asyncio
import discord
import random
import re
from datetime import datetime
import mysql.connector
from discord.ext import commands, tasks
from tabulate import tabulate
from decouple import config

bot = commands.Bot(command_prefix='>')


@bot.event
async def on_ready():
    global old_user
    old_user = bot.user
    birthday_notification.start()
    activity = discord.Activity(name="мультики", type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def prg(ctx, amount=500):
    await ctx.channel.purge(limit=amount + 1)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def sendto(ctx, channel_id: int, everyone: int, *, content):
    await ctx.channel.purge(limit=1)
    if bool(everyone):
        await bot.get_channel(channel_id).send("@everyone\n" + content)
    else:
        await bot.get_channel(channel_id).send(content)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def send(ctx, *, content):
    await ctx.channel.purge(limit=1)
    await ctx.channel.send(content)


seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def mute(ctx, user: discord.Member = None, time: str = '1m'):
    if not user:
        await ctx.send(f"{ctx.message.author.mention}, ты мне скажи, кого замутить то? ")
        return
    clan_chat = bot.get_channel(660800271965880331)
    guest_chat = bot.get_channel(660547830288744494)
    lvl_chat = bot.get_channel(660667529647226890)
    music1 = bot.get_channel(660834112176914442)
    music2 = bot.get_channel(660830929316610068)

    await clan_chat.set_permissions(user, send_messages=False)
    await guest_chat.set_permissions(user, send_messages=False)
    await lvl_chat.set_permissions(user, send_messages=False)
    await music1.set_permissions(user, send_messages=False)
    await music2.set_permissions(user, send_messages=False)
    role = discord.utils.get(ctx.guild.roles, id=760908449227472936)
    await user.add_roles(role)
    await ctx.send(f"{user.mention}, теперь ты {role.name}")

    await asyncio.sleep(int(str(time)[:-1]) * seconds_per_unit[str(time)[-1]])

    await clan_chat.set_permissions(user, send_messages=None)
    await guest_chat.set_permissions(user, send_messages=None)
    await lvl_chat.set_permissions(user, send_messages=None)
    await music1.set_permissions(user, send_messages=None)
    await music2.set_permissions(user, send_messages=None)
    await ctx.send(f"{user.mention} больше не {role.name}\n{role.mention}, минус один")
    await user.remove_roles(role)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def edit(ctx):
    conn = mysql.connector.connect(user=config('DB_user'), password=config('DB_password'),
                                   host=config('DB_host'),
                                   database=config('DB_name'), charset='utf8', autocommit=True)
    cursor = conn.cursor()
    table = []
    main_table = await bot.get_channel(660799528856715300).fetch_message(739440611731439697)
    # main_table------------------------------------------------------------------------
    cursor.execute("SELECT nickname,real_name, DATE_FORMAT(birthday, '%d-%m-%Y'), "
                   "FORMAT((DATE_FORMAT(now(), '%Y')-DATE_FORMAT(birthday, '%Y'))-"
                   "(DATE_FORMAT(now(), '%m-%d')<DATE_FORMAT(birthday, '%m-%d')), 0), "
                   "country, vacation FROM members WHERE vacation='Нет' ORDER BY vacation ASC, id")
    rows = cursor.fetchall()
    rows = [list(_) for _ in rows]
    for row in rows:
        table.append([row[0], row[1], row[2], row[3], row[4], row[5]])
    await main_table.edit(content='@everyone\n' + '```css\n' + tabulate(table,
                                                                        headers=['NICKNAME', 'NAME', 'BIRTHDAY', 'AGE',
                                                                                 'COUNTRY', 'VACATION'],
                                                                        tablefmt="simple",
                                                                        showindex=[x + 1 for x in
                                                                                   range(len(table))]) + '```')
    # vac_table--------------------------------------------------------------------------
    len_main_table = len(table)
    table.clear()
    vac_table = await bot.get_channel(660799528856715300).fetch_message(739440690391679017)
    cursor.execute("SELECT nickname,real_name, DATE_FORMAT(birthday, '%d-%m-%Y'), "
                   "FORMAT((DATE_FORMAT(now(), '%Y')-DATE_FORMAT(birthday, '%Y'))-"
                   "(DATE_FORMAT(now(), '%m-%d')<DATE_FORMAT(birthday, '%m-%d')), 0), "
                   "country, vacation FROM members WHERE vacation!='Нет' ORDER BY vacation ASC, id")
    vac_rows = cursor.fetchall()
    conn.close()
    vac_rows = [list(_) for _ in vac_rows]
    for row in vac_rows:
        table.append([row[0], row[1], row[2], row[3], row[4], row[5]])
    await vac_table.edit(content='```css\n' + tabulate(table,
                                                       headers=['NICKNAME', 'NAME', 'BIRTHDAY', 'AGE',
                                                                'COUNTRY', 'VACATION'],
                                                       tablefmt="simple",
                                                       showindex=[x + len_main_table + 1 for x in
                                                                  range(len(table))]) + '```' + '@everyone')


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def addm(ctx, user: discord.Member, role: str):
    await ctx.channel.purge(limit=1)
    await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name='◈═══════◈Гость◈═══════◈'))
    await user.add_roles(discord.utils.get(ctx.message.guild.roles, name='●────────●Клан●────────●'))
    await user.add_roles(discord.utils.get(ctx.message.guild.roles, name='▬▬▬▬▬●Equilibrium●▬▬▬▬▬'))
    await user.add_roles(discord.utils.get(ctx.message.guild.roles, id=727298785654472776))
    await user.add_roles(discord.utils.get(ctx.message.guild.roles, id=727299629372145684))
    await user.add_roles(discord.utils.find(lambda r: role in r.name, ctx.message.guild.roles))
    # news
    await bot.get_channel(660797576362328066).send(f"@everyone\nПриветствуем нового участника клана - <@{user.id}>")
    emb = discord.Embed(colour=discord.Color.dark_blue())
    emb.add_field(name="Здравствуй!", value="1. Подай заявку на вступление в клан\n"
                                            "https://excalibur-craft.ru/index.php?do=clans&go=profile&id=3717\n"
                                            "2. Вступи в сообщество клана на форуме\n"
                                            "https://forum.excalibur-craft.ru/clubs/68-equilibrium/")
    emb.set_footer(text="Добро пожаловать!")
    # clan-chat
    await bot.get_channel(660800271965880331).send(f"<@{user.id}>", embed=emb)
    try:
        add_user_to_db(user)
    except:
        await bot.get_channel(660808504646303744).send(
            f"Что-то пошло не так, вызывайте экзорциста <@{456951428397924352}>!")
    await edit(ctx)


@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send(f'{ctx.author.mention}, ДА РАБОТАЮ Я, ОТВАЛИ!')


@bot.event
async def on_message(message):
    guild = message.guild
    if message.channel.id == 727293535727911566:
        try:
            color_role = discord.utils.get(guild.roles, id=727299629372145684)
            perms_role = discord.utils.get(guild.roles, id=727298785654472776)
            user = message.author
            content = message.content
            if ' ' in content:
                content = content.replace(' ', '')
            if '#' not in content:
                content = '#' + content
            color_name = content
            role_create = False
            for r in guild.roles:
                if r.name.lower() in color_name.lower():
                    new_role = r
                    role_create = True
            if not role_create:
                new_role = await guild.create_role(name=color_name,
                                                   colour=discord.Colour(int(color_name.replace('#', '0x'), 16)))
                await new_role.edit(position=random.randint(perms_role.position + 1, color_role.position - 1))
            if color_role in user.roles:
                for _ in range(len(user.roles)):
                    if user.roles[_].name == color_role.name:
                        if user.roles[_ - 1].name == perms_role.name:
                            pass
                        else:
                            await user.remove_roles(user.roles[_ - 1])
                        await user.add_roles(new_role)
                        break
            else:
                await user.add_roles(color_role)
                await user.add_roles(new_role)
            await message.add_reaction(bot.get_emoji(id=662134292058734614))
        except:
            await message.add_reaction(bot.get_emoji(id=662134317446725633))
    else:
        pass
    await bot.process_commands(message)


def find_clan(guild: discord.Guild, clan_name: str) -> discord.Role:
    clans = ['▬▬▬▬▬▬●Quasar●▬▬▬▬▬▬', '▬▬▬▬▬▬●BestLife●▬▬▬▬▬▬', '▬▬▬▬▬●AVALON●▬▬▬▬▬',
             '▬▬▬▬▬▬●Pride●▬▬▬▬▬▬', '▬▬▬▬▬▬●PrimalZ●▬▬▬▬▬▬', '▬▬▬▬▬▬●Mortes●▬▬▬▬▬▬',
             '▬▬▬▬▬▬●Ordo●▬▬▬▬▬▬', '▬▬▬▬▬●DarkElite●▬▬▬▬▬', '▬▬▬▬▬▬●Rise●▬▬▬▬▬▬']
    clan_role = [discord.utils.get(guild.roles, name=c) for c in clans if clan_name.lower() in c.lower()]
    return clan_role[0]


async def authorize(guild: discord.Guild, user: discord.Member, message: str):
    await user.edit(nick=f'{message[0].split(".")[1]} [{message[2].split(".")[1]}]')
    await user.add_roles(discord.utils.get(guild.roles, id=660617694118150184))  # Equilibrium_guest
    try:
        await user.add_roles(find_clan(guild, message[1].split(".")[1]))  # off. clan role
        await user.add_roles(discord.utils.get(guild.roles, id=660599549802577984))  # clan_role
        await user.add_roles(discord.utils.get(guild.roles, id=683415819409293386))  # selector
    except:
        pass
    await user.remove_roles(discord.utils.get(guild.roles, id=662080379330494474))  # waited


@bot.event
async def on_raw_reaction_add(payload):
    global old_user
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)
    bot_user = guild.get_member(691690627259432981)
    auth_channel = bot.get_channel(662083817833627722)
    if payload.channel_id == auth_channel.id:
        history = await auth_channel.history(limit=100).flatten()
        msg = await auth_channel.fetch_message(payload.message_id)
        for message in history:
            if message.id == msg.id:
                msg = message
                break
        if msg.author is bot_user:
            bot_message = msg
            user_message = history[(history.index(msg)) - 1]
        else:
            user_message = msg
            bot_message = history[(history.index(msg)) + 1]
        if payload.emoji == bot.get_emoji(662134292058734614):  # accept
            content = user_message.content
            if ' ' in content:
                content = content.replace(' ', '')
            msg = content.split("\n")
            await authorize(guild, user_message.author, msg)
            await user_message.delete()
            await bot_message.delete()
        elif payload.emoji == bot.get_emoji(662134317446725633):  # deny
            await user_message.author.remove_roles(discord.utils.get(guild.roles, id=662080379330494474))  # waited
            await user_message.delete()
            await bot_message.delete()
            await user_message.author.create_dm()
            await user_message.author.dm_channel.send("Что-то пошло не так, твоя анкета нам не понравилась...")
        else:
            pass
    elif payload.channel_id == 660665545800024083:
        if len(user.roles) > 1:
            yui_channel = bot.get_channel(660665545800024083)
            await yui_channel.set_permissions(user, read_messages=False)
            await user.remove_roles(discord.utils.get(guild.roles, id=662080379330494474))  # waited
        else:
            if old_user and user == old_user:
                await user.create_dm()
                await user.dm_channel.send("Уупсс...\nКажется у тебя забрали доступ к авторизации, обратись к Zzz#9909")
                yui_channel = bot.get_channel(660665545800024083)
                await yui_channel.set_permissions(user, read_messages=False)
                await user.remove_roles(discord.utils.get(guild.roles, id=662080379330494474))  # waited
            else:
                old_user = user
                welcome_message = await auth_channel.send(f'Привет, {user.mention}!\n'
                                                          f'Форма анкеты для авторизации на сервере(одним сообщением, обязательно!):\n'
                                                          f'1. Nickname\n2. Clan\n3. Name\nПример анкеты:\n'
                                                          f'1. Kreg78\n2. Equilibrium\n3. Тимур\nПоставьте прочерк "-" на втором пункте, '
                                                          f'если Вы не состоите в клане.\nСоблюдение формы обязательно, потому что '
                                                          f'авторизация производится автоматически мной(ботом)!\n'
                                                          f'*при несоблюдении формы анкеты Вас не авторизуют.')

                def check(message):
                    return user == message.author

                try:
                    message = await bot.wait_for('message', check=check, timeout=300)
                except asyncio.TimeoutError:
                    await user.remove_roles(discord.utils.get(guild.roles, id=662080379330494474))  # waited
                    await welcome_message.delete()
                else:
                    pass


def add_user_to_db(user):
    conn = mysql.connector.connect(user=config('DB_user'), password=config('DB_password'),
                                   host=config('DB_host'),
                                   database=config('DB_name'), charset='utf8', autocommit=True)
    cursor = conn.cursor()
    nickname = re.search(r'[^\W*]\w+', user.display_name)[0]
    real_name = re.search(r'(?<=\[).+?(?=\])', user.display_name)[0]
    cursor.execute(f"SELECT nickname FROM members where nickname='{nickname}'")
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO members(nickname, real_name, id, vacation) select ?,?,max(id)+1,'Нет' from members",
            (nickname, real_name,))
    else:
        pass
    conn.commit()
    conn.close()


@commands.has_permissions(administrator=True)
@bot.command(pass_context=True)
async def change(ctx, nickname: str, *, args: str):
    conn = mysql.connector.connect(user=config('DB_user'), password=config('DB_password'),
                                   host=config('DB_host'),
                                   database=config('DB_name'), charset='utf8', autocommit=True)
    cursor = conn.cursor()
    arg = args.split('=')
    if arg[0] == 'id':
        cursor.execute(f"update members set id=id+1 where id>={int(arg[1])} and "
                       f"id<(select id from members where nickname=%s)", (nickname,))
        cursor.execute(f"update members set id={int(arg[1])} where nickname=%s", (nickname,))
    elif arg[0] == 'birthday':
        cursor.execute(f"UPDATE members SET {''.join(arg[0])}={datetime.strptime(arg[1], '%Y-%m-%d')} "
                       f"where nickname=%s", (nickname,))
    else:
        cursor.execute(f"UPDATE members SET {''.join(arg[0])}={arg[1]} where nickname=%s", (nickname,))
    conn.commit()
    conn.close()
    await edit(ctx)


@commands.has_permissions(administrator=True)
@bot.command(pass_context=True)
async def cmd(ctx, *, command: str):
    conn = mysql.connector.connect(user=config('DB_user'), password=config('DB_password'),
                                   host=config('DB_host'),
                                   database=config('DB_name'), charset='utf8', autocommit=True)
    cursor = conn.cursor()
    cursor.execute(f"{''.join(command)}")
    conn.commit()
    conn.close()


@commands.has_permissions(administrator=True)
@bot.command(pass_context=True)
async def remove(ctx, nickname: str):
    conn = mysql.connector.connect(user=config('DB_user'), password=config('DB_password'),
                                   host=config('DB_host'),
                                   database=config('DB_name'), charset='utf8', autocommit=True)
    cursor = conn.cursor()
    cursor.execute(f"update members set id=id-1 where id>(select id from members "
                   f"where nickname=%s)", (nickname,))
    cursor.execute(f"delete from members where nickname=%s", (nickname,))
    conn.commit()
    conn.close()
    await edit(ctx)


@bot.command(pass_context=True)
async def poll(ctx):
    await ctx.message.add_reaction(bot.get_emoji(662134317446725633))  # deny
    await ctx.message.add_reaction(bot.get_emoji(662134292058734614))  # accept


@tasks.loop(hours=24)
async def birthday_notification():
    conn = mysql.connector.connect(user=config('DB_user'), password=config('DB_password'),
                                   host=config('DB_host'),
                                   database=config('DB_name'), charset='utf8', autocommit=True)
    cursor = conn.cursor()
    channel = bot.get_channel(660797576362328066)  # news
    emoji = bot.get_emoji(733391075208593479)
    message = f' сегодня День Рождения{emoji}\nОт всего нашего мини сообщества, поздравляем тебя с этим днем!'
    bday = []
    cursor.execute(f"select DATE_FORMAT(birthday, '%d-%m') from members")
    dates = cursor.fetchall()
    dates = [list(_) for _ in dates]
    for row in dates:
        bday.append(row[0])
    today = datetime.strftime(datetime.now(), '%d-%m')
    if today in bday:
        cursor.execute(f"select nickname from members "
                       f"where (DATE_FORMAT(birthday, '%d-%m'))=%s", (today,))
        nicknames = cursor.fetchall()
        nicknames = [list(_) for _ in nicknames]
        for row in nicknames:
            user = discord.utils.find(lambda u: row[0] in u.display_name, channel.guild.members)
            await channel.send('@everyone, у ' + user.mention + message)
    else:
        pass
    conn.close()


@birthday_notification.before_loop
async def before():
    f = '%H:%M'
    now = datetime.strftime(datetime.now(), f)
    diff = (datetime.strptime('09:00', f) - datetime.strptime(now, f)).total_seconds()
    if diff < 0:
        diff += 86400
    await asyncio.sleep(diff)


bot.run(config('DAB_TOKEN'))
