import requests, re, discordfrom discord.ext import commandsfrom bs4 import BeautifulSoupfrom langdetect import detectimport datetimeimport pytzimport asyncioTOKEN = 'NjkxNjkwNjI3MjU5NDMyOTgx.XnjpXg.3j1SyoRnS_8BX5dkJ7pRiOntlEg'log_url = 'https://forum.excalibur-craft.ru/login/'url = 'https://forum.excalibur-craft.ru/topic/125632-equilibrium/'url_edit = 'https://forum.excalibur-craft.ru/topic/125214-for-mkzet/'bot = commands.Bot(command_prefix='|')@bot.eventasync def on_ready():    activity = discord.Activity(name="SumbiT'a", type=discord.ActivityType.listening)    await bot.change_presence(activity=activity)    await vcmembers()def add(math):    data = int(math[0].split('+')[0]) + int(math[0].split('+')[1])    return {'answer': str(data)}def login(session):    req = session.get(log_url)    math = re.findall('Вопрос: (.*?) =', req.text)    req_f = session.post(log_url, add(math))    csrf = re.findall('name="csrfKey".*?value="(.*?)"', req_f.text)    text = session.get(        f'''https://forum.excalibur-craft.ru/login/?csrfKey={csrf[0]}&auth=exlord&password=Kola_2102_&remember_me=1&_        processLogin=usernamepassword&_processLogin=usernamepassword''')    return textdef parse_post(text, find_nick, comment_url=None):    posts = text.find_all('article', {'class': ['cPost', 'ipsComment']})    post = []    for _ in posts:        nick_bd_write = open('nicks.txt', 'a')        nick_bd_read = open('nicks.txt', 'r')        nick_list = nick_bd_read.read().split('\n')        nick = str(_.find('div', {'class': 'cAuthorPane'}).find('a').text)        if nick in nick_list:            if nick == str(find_nick):                post.append(str(_.find('div', {'data-role': 'commentContent'}).text).replace('\t', '').replace('\n\n\n', '\n'))                if comment_url is not None:                    comment_url.append(str(_.find('a', {'data-action': 'editComment'}).get('href')))                return post            continue        else:            nick_bd_write.write(nick+'\n')            nick_bd_write.close()            post.append(str(_.find('div', {'data-role': 'commentContent'}).text).replace('\t', '').replace('\n\n\n', '\n'))    return postdef get_post(nick):    s = requests.session()    login(s)    posts = []    page = s.get(url)    rel = True    while 1:        if rel:            soup = BeautifulSoup(page.text, 'html.parser')            posts += parse_post(soup, nick)            rel = bool(soup.find('link', {'rel': 'next'}))            try:                page = s.get(soup.find('link', {'rel': 'next'}).get('href'))            except AttributeError:                pass        else:            soup = BeautifulSoup(page.text, 'html.parser')            posts += parse_post(soup, nick)            break    return posts# def edit_post(nick):#     s = requests.session()#     auth = login(s)#     csrf = re.findall('csrfKey.*?"(.*?)"', auth.text)#     soup = BeautifulSoup(s.get(f'''https://forum.excalibur-craft.ru/topic/125214-for-mkzet/''').text, 'html.parser')#     plupload = soup.find('input', {'name': 'plupload'}).get('value')#     MAX_FILE_SIZE = soup.find('input', {'name': 'MAX_FILE_SIZE'}).get('value')#     edit_url = []#     post = parse_post(soup, nick, edit_url)#     ppost = post[0].replace(' ', ' ').split('\n')##     ppost = [x for x in ppost if (x and len(x) > 2)]#     for _ in range(len(ppost)):#         if 'сказал' in ppost[_] or 'Изменено' in ppost[_]:#             del ppost[_]#     if detect(ppost[0]) == 'ru':#         del ppost[0]##     pg = s.get(f'''{''.join(edit_url)}''',#                params={#                        'form_submitted': '1',#                        'csrfKey': csrf[2],#                        'MAX_FILE_SIZE': MAX_FILE_SIZE,#                        'plupload': plupload,#     'comment_value': f'''[font=CONSOLAS][left]{ppost[0]}[left]# [left]{ppost[1]}[/left]# [left]{ppost[2]}[/left]# [left]{ppost[3]}[/left]# [left]{ppost[4]}[/left]# [left]{ppost[5]}[/left]# [left]{ppost[6]}[/left]# [left]{ppost[7]}[/left]# [left]{ppost[8]}[/left]# [left]{ppost[9]}[/left][/font]# [center][img]https://i.ibb.co/wLWh9Xk/accept.png[/img][/center]'''})@bot.command(pass_context=True)@commands.has_role("Admin*")async def clear(ctx, amount=500):    await ctx.channel.purge(limit=amount+1)    # channel = ctx.message.channel    # messages = []    # async for message in channel.history(limit=amount):    #     messages.append(message)    # await channel.delete_messages(messages)# @bot.command(pass_context=True)# @commands.has_role("Admin*")# async def get(ctx, nick=''):#     await ctx.channel.purge(limit = 1)#     if len(nick) >= 3:#         await ctx.send(get_post(nick)[0])#     else:#         for post in get_post(nick):#             msg = await ctx.send(post)#'@everyone'+#             await msg.add_reaction('❌')#             await msg.add_reaction('✅')#@bot.command()#async def edit(ctx, nick):    # try:    #     edit_post(nick)    #     await ctx.send('all ok!')    # except requests.exceptions.MissingSchema:    #     await ctx.send(f'"{nick}" not found')@bot.command(pass_context=True)@commands.has_role("Admin*")async def addm(ctx, user: discord.Member, role: str):    await ctx.channel.purge(limit=1)    await user.remove_roles(discord.utils.get(ctx.message.guild.roles, name='◈═══════◈Гость◈═══════◈'))    await user.add_roles(discord.utils.get(ctx.message.guild.roles, name='●────────●Клан●────────●'))    await user.add_roles(discord.utils.get(ctx.message.guild.roles, name='▬▬▬▬▬●Equilibrium●▬▬▬▬▬'))    role_n = discord.utils.find(lambda r: role in r.name, ctx.message.guild.roles)    await user.add_roles(role_n)    id = user.id    await ctx.send(f"Эй @everyone, <@{id}> теперь {role_n.name}")@bot.command(pass_context=True)@commands.has_role("Admin*")async def delm(ctx, user: discord.Member):    await ctx.channel.purge(limit=1)    id = user.id    await ctx.send(f"Эй @everyone, <@{id}> покинул нас.")    await user.add_roles(discord.utils.get(ctx.guild.roles, name='◈═══════◈Гость◈═══════◈'))    await user.remove_roles(discord.utils.get(ctx.guild.roles, name='●────────●Клан●────────●'))    await user.remove_roles(discord.utils.get(ctx.guild.roles, name='▬▬▬▬▬●Equilibrium●▬▬▬▬▬'))    if '═◈' in user.roles[-1].name:        await user.remove_roles(user.roles[-1])    else:        await user.remove_roles(user.roles[-2])@bot.command(pass_context = True)async def vcmembers():    voice = discord.utils.find(lambda v: 'Голосовой онлайн:' in v.name, bot.get_all_channels())    time = discord.utils.find(lambda v: 'Московское время' in v.name, bot.get_all_channels())    #time = await ctx.guild.create_voice_channel(f"Московское время - {datetime.datetime.now().hour}:{datetime.datetime.now().minute}")    voice_channel_list = bot.guilds[0].voice_channels    # getting the members in the voice channel    while True:        await time.edit(name=f"Московское время {datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%H:%M')}")        members = 0 #{datetime.datetime.now().hour}:{datetime.datetime.now().minute}        for voice_channels in voice_channel_list:            # list the members if there are any in the voice channel            if len(voice_channels.members) != 0:                members += len(voice_channels.members)        await voice.edit(name=f" Голосовой онлайн: {members}")@bot.command(pass_context=True)async def banan(ctx, member: discord.Member):    if str(ctx.author.id) == '517349425371414538':        await ctx.send(f'{member.mention} has been bananned by {ctx.author.name}!')    else:        await ctx.send(f"{ctx.author.mention}, бык?!")@bot.eventasync def on_message(message):    if message.channel.name == "📩доступ":        emj = bot.get_emoji(id=662134292058734614)        def check(reaction, user):            return user.id == (456951428397924352 or 247029882519945218 or 269165112516935680 or 517349425371414538)\                   and reaction.emoji == emj        async def add_role(content):            if ' ' in content:                content = content.replace(' ', '')            msg = content.split("\n")            await message.author.edit(nick=f'{msg[0].split(".")[1]} [{msg[2].split(".")[1]}]')            await message.author.remove_roles(discord.utils.get(bot.guilds[0].roles, id=662080379330494474))            await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, name='◈═══════◈Гость◈═══════◈'))            await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, id=660598561536475146))            await message.author.add_roles(                discord.utils.get(bot.guilds[0].roles, name='●─────●Игровые роли●─────●'))            clans = ['▬▬▬▬▬▬●Quasar●▬▬▬▬▬▬', '▬▬▬▬▬▬●BestLife●▬▬▬▬▬▬', '▬▬▬▬▬●AVALON●▬▬▬▬▬',                     '▬▬▬▬▬▬●Pride●▬▬▬▬▬▬', '▬▬▬▬▬▬●PrimalZ●▬▬▬▬▬▬', '▬▬▬▬▬▬●Mortes●▬▬▬▬▬▬',                     '▬▬▬▬▬▬●Ordo●▬▬▬▬▬▬', '▬▬▬▬▬●DarkElite●▬▬▬▬▬', '▬▬▬▬▬▬●Rise●▬▬▬▬▬▬',                     '▬▬▬▬▬▬●Revolt●▬▬▬▬▬▬', '▬▬▬▬▬●LostParadise●▬▬▬▬▬']            clan = ''.join([c for c in clans if msg[1].split(".")[1] in c])            if clan:                await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, id=683415819409293386))                await message.author.add_roles(                    discord.utils.get(bot.guilds[0].roles, name='●────────●Клан●────────●'))                await message.author.add_roles(discord.utils.get(bot.guilds[0].roles, name=clan))        try:            reaction, user = await bot.wait_for('reaction_add', check=check)        except asyncio.TimeoutError:            await message.channel.send('👎')        else:            #users = await reaction.users().flatten()            if "\n" in message.content:                await add_role(message.content)            else:                channel = message.channel                messages = []                async for msg in channel.history(limit=3):                    messages.append(msg.content)                messages.reverse()                ms = ''                for m in messages:                    ms += m + '\n'                await add_role(ms)    await bot.process_commands(message)bot.run(TOKEN)