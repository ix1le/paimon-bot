# Version 3.6

# Imports
import discord
from discord.ext import commands
from pymongo import MongoClient
from ruamel.yaml import YAML
import vacefron
from re import search


# MONGODB SETTINGS *YOU MUST FILL THESE OUT OTHERWISE YOU'LL RUN INTO ISSUES!* - Need Help? Join The Discord Support Server, Found at top of repo.
cluster = MongoClient("mongodb+srv://niron:tf2freeze@cluster0.ywhuv.mongodb.net/discord?retryWrites=true&w=majority")
levelling = cluster["discord"]["lvldb"]

# Reads the config file, no need for changing.
yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)

# Some config options which need to be stored here, again, no need for altering.
bot_channel = config['bot_channel']
talk_channels = config['talk_channels']
level_roles = config['level_roles']
level_roles_num = config['level_roles_num']

# Vac-API, no need for altering!
vac_api = vacefron.Client()


class levelsys(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Уровни были подгружены.')


    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.channel.id in config['talk_channels']:
            stats = levelling.find_one({"id": ctx.author.id})
            if not ctx.author.bot:
                if stats is None:
                    newuser = {"id": ctx.author.id, "tag": ctx.author.mention, "xp": 0, "rank": 1, "background": " ",
                               "circle": False, "xp_colour": "#ffffff"}
                    print(f"Участник: {ctx.author.id} был добавлен в базу данных! ")
                    levelling.insert_one(newuser)
                else:
                    if config['Prefix'] in ctx.content:
                        stats = levelling.find_one({"id": ctx.author.id})
                        xp = stats["xp"]
                        levelling.update_one({"id": ctx.author.id}, {"$set": {"xp": xp}})
                    else:
                        user = ctx.author
                        role = discord.utils.get(ctx.guild.roles, name=config['double_xp'])
                        if role in user.roles:
                            xp = stats["xp"] + config['xp_per_message'] * 2
                            levelling.update_one({"id": ctx.author.id}, {"$set": {"xp": xp}})
                        else:
                            xp = stats["xp"] + config['xp_per_message']
                            levelling.update_one({"id": ctx.author.id}, {"$set": {"xp": xp}})
                    lvl = 0
                    while True:
                        if xp < ((config['xp_per_level'] / 2 * (lvl ** 2)) + (config['xp_per_level'] / 2 * lvl)):
                            break
                        lvl += 1
                    xp -= ((config['xp_per_level'] / 2 * ((lvl - 1) ** 2)) + (config['xp_per_level'] / 2 * (lvl - 1)))
                    if xp == 0:
                        levelling.update_one({"id": ctx.author.id}, {"$set": {"rank": + config['xp_per_message']}})
                        embed2 = discord.Embed(title=f":tada: **Уровень повышен!**",
                                               description=f"{ctx.author.mention} заработал: **{lvl}** уровень",
                                               colour=config['embed_colour'])
                        xp = stats["xp"]
                        levelling.update_one({"id": ctx.author.id},
                                             {"$set": {"rank": lvl, "xp": xp + config['xp_per_message'] * 2}})
                        print(f"Участник: {ctx.author} | Повысил уровень: {lvl}")
                        embed2.add_field(name="До следущего уровня:",
                                         value=f"``{int(config['xp_per_level'] * 2 * ((1 / 2) * lvl))}xp``")
                        embed2.set_thumbnail(url=ctx.author.avatar_url)
                        await ctx.channel.send(embed=embed2)
                        for i in range(len(level_roles)):
                            if lvl == level_roles_num[i]:
                                await ctx.author.add_roles(
                                    discord.utils.get(ctx.author.guild.roles, name=level_roles[i]))
                                embed = discord.Embed(title=":tada: **Разблокирована роль!**",
                                                      description=f"{ctx.author.mention} разблокировал **{level_roles[i]}** роль!",
                                                      colour=config['embed_colour'])
                                print(f"Участник: {ctx.author} | Разблокировал роль: {level_roles[i]}")
                                embed.set_thumbnail(url=ctx.author.avatar_url)
                                await ctx.channel.send(embed=embed)
    # Rank Command
    @commands.command(aliases=config['rank_alias'])
    async def rank(self, ctx):
        member = ctx.author
        if ctx.channel.id in config['bot_channel']:
            stats = levelling.find_one({"id": ctx.author.id})
            if stats is None:
                embed = discord.Embed(description=":x: Вас нет в базе данных, я не могу показать ваш уровень!",
                                      colour=config['error_embed_colour'])
                await ctx.channel.send(embed=embed)
            else:
                xp = stats["xp"]
                lvl = 0
                rank = 0
                while True:
                    if xp < ((config['xp_per_level'] / 2 * (lvl ** 2)) + (config['xp_per_level'] / 2 * lvl)):
                        break
                    lvl += 1
                xp -= ((config['xp_per_level'] / 2 * (lvl - 1) ** 2) + (config['xp_per_level'] / 2 * (lvl - 1)))
                boxes = int((xp / (config['xp_per_level'] * 2 * ((1 / 2) * lvl))) * 20)
                rankings = levelling.find().sort("xp", -1)
                for x in rankings:
                    rank += 1
                    if stats["id"] == x["id"]:
                        break
                if config['image_mode'] is False:
                    embed = discord.Embed(title="{}'s Stats Menu | :bar_chart: ".format(ctx.author.name),
                                          colour=config['rank_embed_colour'])
                    embed.add_field(name="Name", value=ctx.author.mention, inline=True)
                    embed.add_field(name="XP",
                                    value=f"{xp}/{int(config['xp_per_level'] * 2 * ((1 / 2) * lvl))}",
                                    inline=True)
                    embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}", inline=True)
                    embed.add_field(name="Progress Bar",
                                    value=boxes * config['completed_bar'] + (20 - boxes) * config['uncompleted_bar'],
                                    inline=False)
                    embed.add_field(name=f"Level", value=f"{lvl}", inline=False)
                    embed.set_thumbnail(url=ctx.message.author.avatar_url)
                    await ctx.channel.send(embed=embed)
                elif config['image_mode'] is True:
                    background = stats["background"]
                    circle = stats["circle"]
                    xpcolour = stats["xp_colour"]
                    avatar = member.avatar_url_as(format="png")
                    avatar_size_regex = search("\?size=[0-9]{3,4}$", str(avatar))
                    avatar = str(avatar).strip(str(avatar_size_regex.group(0))) if avatar_size_regex else str(avatar)
                    gen_card = await vac_api.rank_card(
                        username=str(member),
                        avatar=avatar,
                        level=int(lvl),
                        rank=int(rank),
                        current_xp=int(xp),
                        next_level_xp=int(config['xp_per_level'] * 2 * ((1 / 2) * lvl)),
                        previous_level_xp=0,
                        xp_color=str(xpcolour),
                        custom_background=str(background),
                        is_boosting=bool(member.premium_since),
                        circle_avatar=circle
                    )
                    embed = discord.Embed(colour=config['rank_embed_colour'])
                    embed.set_image(url=gen_card.url)
                    await ctx.send(embed=embed)

    # Leaderboard Command
    @commands.command(aliases=config['leaderboard_alias'])
    async def leaderboard(self, ctx):
        if ctx.channel.id in bot_channel:
            rankings = levelling.find().sort("xp", -1)
            i = 1
            con = config['leaderboard_amount']
            embed = discord.Embed(title=f":trophy: Топ рейтинга участников | Топ {con}", colour=config['leaderboard_embed_colour'])
            for x in rankings:
                try:
                    temp = ctx.guild.get_member(x["id"])
                    tempxp = x["xp"]
                    templvl = x["rank"]
                    embed.add_field(name=f"#{i}: {temp.name}",
                                    value=f"Уровень: ``{templvl}``\nТекущее XP: ``{tempxp}``\n", inline=True)
                    embed.set_thumbnail(url=config['leaderboard_image'])
                    i += 1
                except:
                    pass
                if i == config['leaderboard_amount'] + 1:
                    break
            await ctx.channel.send(embed=embed)

    # Reset Command
    @commands.command()
    @commands.has_role(config["admin_role"])
    async def reset(self, ctx, user=None):
        if user:
            userget = user.replace('!', '')
            levelling.update_one({"tag": userget}, {"$set": {"rank": 1, "xp": config['xp_per_message']}})
            embed = discord.Embed(title=f":white_check_mark: RESET USER", description=f"Reset User: {user}",
                                  colour=config['success_embed_colour'])
            print(f"{userget} was reset!")
            await ctx.send(embed=embed)
        else:
            prefix = config['Prefix']
            embed2 = discord.Embed(title=f":x: RESET USER FAILED",
                                   description=f"Couldn't Reset! The User: ``{user}`` doesn't exist or you didn't mention a user!",
                                   colour=config['error_embed_colour'])
            embed2.add_field(name="Example:", value=f"``{prefix}reset`` {ctx.message.author.mention}")
            print("Resetting Failed. A user was either not declared or doesn't exist!")
            await ctx.send(embed=embed2)

    # Help Command
    @commands.command(aliase="h")
    async def help(self, ctx):
        if config['help_command'] is True:
            prefix = config['Prefix']
            top = config['leaderboard_amount']
            xp = config['xp_per_message']

            embed = discord.Embed(title="**Помощь по командам | :book:**",
                                  colour=config["embed_colour"])
            embed.add_field(name="Рейтинг:", value=f"``{prefix}leaderboard`` Показывает Топ: **{top}** участников.")
            embed.add_field(name="Уровень:", value=f"`{prefix}rank` Показывает вашу статистику.")
            embed.add_field(name="Сброс:",
                            value=f"``{prefix}reset <user>`` Устанавливает участнику обратно: `{config['xp_per_message']}` xp & `1` уровень.")
            embed.add_field(name="Фон:",
                            value=f"``{prefix}background <link>`` Изменяет фон вашей карточки, если включен `image_mode`.")
            embed.add_field(name="Рамка:",
                            value=f"``{prefix}circlepic <True|False>`` Изменяет изооброжение пользователя на круг в карточке, если включен `image_mode`.")
            embed.add_field(name="Обновить базу данных:",
                            value=f"``{prefix}update <user>`` Обновляет любые отсутствующие поля базы данных пользоватей, для обновлении до более новой версии.")
            embed.add_field(name="Полоска опыта:",
                            value=f"``{prefix}xpcolor <hex code>`` Изменяет цвет полосы опыта, если включен режим `image_mode`.")
            embed.add_field(name="Поддержка:",
                            value=f"``{prefix}support <text>`` написать в службу поддержки.")
            embed.set_footer(text=f"")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/820366287175155732/826918201291178065/standard.gif")
            await ctx.channel.send(embed=embed)

    @commands.command()
    @commands.has_role("🍀 Заместитель Руководителя")
    async def restart(self, ctx):
        exit("Перезагрузка..")

    @commands.command()
    async def background(self, ctx, link):
        levelling.update_one({"id": ctx.author.id}, {"$set": {"background": f"{link}"}})
        embed = discord.Embed(title=":white_check_mark: **Фон вашей карточки изменен!**",
                              description="Фон вашей карточки успешно настроен! Если ваш фон не обновляется, попробуйте новое изображение.")
        embed.set_thumbnail(url=link)
        await ctx.channel.send(embed=embed)

    @commands.command()
    async def circlepic(self, ctx, value):
        if value == "true":
            levelling.update_one({"id": ctx.author.id}, {"$set": {"circle": True}})
            embed1 = discord.Embed(title=":white_check_mark: **Изменения прошли успешно!**",
                                   description="Для изображения в вашей карточки, установлено круглое значение: ``True``. Поставте ``False`` чтобы вертнутся к стандартному значению..")
            await ctx.channel.send(embed=embed1)
        elif value == "false":
            levelling.update_one({"id": ctx.author.id}, {"$set": {"circle": False}})
            embed2 = discord.Embed(title=":white_check_mark: **Изменения прошли успешно!**",
                                   description="Для изображения в вашей карточки, установлено стандартное значение: ``False``. Поставте ``True`` чтобы изменить изооброжение пользователя на круг в карточке..")
            await ctx.channel.send(embed=embed2)

    @commands.command()
    async def xpcolor(self, ctx, colour):
        if colour is None:
            embed = discord.Embed(title=":x: **Что-то пошло не так!**",
                                  description="Убедитесь, что вы ввели hex code!")
            await ctx.channel.send(embed=embed)
            return
        levelling.update_one({"id": ctx.author.id}, {"$set": {"xp_colour": f"{colour}"}})
        prefix = config['Prefix']
        embed = discord.Embed(title=":white_check_mark: **Полоска опыта изменена!**",
                              description=f"Цвет полоски опыта, была успешно изменена. Если вы набираете ``{prefix}rank`` и ничего не изменится, попробуйте другой hex code.\n**Пример**:\n*#0000FF* = *Blue*")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/820366287175155732/826918201291178065/standard.gif")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(config["admin_role"])
    async def update(self, ctx, user=None):
        if user:
            levelling.update_one({"id": ctx.author.id}, {"$set": {"background": "", "circle": False, "xp_colour": "#ffffff"}})
            embed = discord.Embed(title=f":white_check_mark: UPDATED USER", description=f"Updated User: {user}",
                                  colour=config['success_embed_colour'])
            await ctx.send(embed=embed)
        else:
            prefix = config['Prefix']
            embed2 = discord.Embed(title=f":x: UPDATE USER FAILED",
                                   description=f"Couldn't Update User: ``{user}`` doesn't exist or you didn't mention a user!",
                                   colour=config['error_embed_colour'])
            embed2.add_field(name="Example:", value=f"``{prefix}update`` {ctx.message.author.mention}")
            await ctx.send(embed=embed2)

def setup(client):
    client.add_cog(levelsys(client))

# End Of Level System

