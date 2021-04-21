# Version 3.4

# Imports
from discord.ext import commands
from discord.ext.commands import CommandNotFound, MissingRequiredArgument, CommandInvokeError, MissingRole
import discord
from ruamel.yaml import YAML
import logging
from asyncio import sleep
import os
import asyncio
import sys
import aiofiles
from discord import DMChannel

import datetime
import time

# Opens the config and reads it, no need for changes unless you'd like to change the library (no need to do so unless having issues with ruamel)
yaml = YAML()
with open("configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


# Command Prefix + Removes the default discord.py help command
client = commands.Bot(command_prefix=config['Prefix'], intents=discord.Intents.all(), case_insensitive=True)
client.remove_command('help')

# If enabled, will send discord logging files which could potentially be useful for catching errors.
if config['enable_log'] is True:
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='Logs/logs.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


@client.event  # On Bot Startup, Will send some details about the bot and sets it's activity and status. Feel free to remove the print messages, but keep everything else.
async def on_ready():
    config_status = config['bot_status_text']
    config_activity = config['bot_activity']
    activity = discord.Game(name=config['bot_status_text'])
    print('\n------')
    print('Бот запущен:')
    print(f"Имя бота: {client.user.name}\nID: {client.user.id}")
    print('------')
    print(f"Установлен статус: {config_status}\nАктивность: {config_activity}")
    print("------")
    await client.change_presence(status=config_activity, activity=activity)


# If enabled in config, will send a welcome message + adds a role if a new user joins the guild (if roles are enabled).
@client.event
async def on_member_join(member):
    if config['join_leave_message'] is True:
        channel = client.get_channel(config['join_leave_channel'])
        embed = discord.Embed(title=f"**:man_raising_hand: WELCOME**", description=f"Welcome **{member.mention}** to **{member.guild.name}**!", colour=discord.Colour.green())
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.guild.icon_url)
        await channel.send(embed=embed)
        if config['add_role'] is True:
            rank = discord.utils.get(member.guild.roles, name=config['on_join_role'])
            await member.add_roles(rank)
            print(f"User: {member} was given the {rank} role.")


# If enabled in config, will send a leave message if a user leaves the guild
@client.event
async def on_member_remove(member):
    if config['join_leave_message'] is True:
        channel = client.get_channel(config['join_leave_channel'])
        embed = discord.Embed(title=f"**:man_raising_hand: GOODBYE**", description=f"**{member.mention}** has left **{member.guild.name}**!", colour=discord.Colour.red())
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.guild.icon_url)
        await channel.send(embed=embed)


@client.event  # Stops Certain errors from being thrown in the console (Don't remove as it'll cause command error messages to not send! - Only remove if adding features and needed for testing (Don't forget to re-add)!)
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, MissingRequiredArgument):
        return
    if isinstance(error, CommandInvokeError):
        return
    if isinstance(error, MissingRole):
        return
    if isinstance(error, AttributeError):
        return
    raise error

@client.command()
async def load(ctx, extension):
    if ctx.author.id == 704649187433644032 or 628999674812170251:
        bot.load_extension(f'cogs.{extension}')
        embed = discord.Embed(description = f'Включениеᅠкогаᅠ`{extension}.py`', colour=discord.Color.from_rgb(47, 49, 54))
        msg = await ctx.send(embed = embed)
        time.sleep(1)
        await msg.add_reaction('✅')
    else:
        embed = discord.Embed(description = f'У вас нет прав для выполнения данной операции', colour=discord.Color.from_rgb(47, 49, 54))
        await ctx.send(embed = embed)

@client.command()
async def reload(ctx, extension):
    if ctx.author.id == 704649187433644032 or 628999674812170251:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        embed = discord.Embed(description = f'Перезагрузка когаᅠ`{extension}.py`', colour=discord.Color.from_rgb(47, 49, 54))
        msg = await ctx.send(embed = embed)
        time.sleep(1)
        await msg.add_reaction('✅')
    else:
        await ctx.send('У вас нет прав для выполнения данной операции',)
        
@client.command()
async def unload(ctx, extension):
    if ctx.author.id == 704649187433644032 or 628999674812170251:
        bot.unload_extension(f'cogs.{extension}')
        embed = discord.Embed(description = f'Отключениеᅠкогаᅠ`{extension}.py`', colour=discord.Color.from_rgb(47, 49, 54))
        msg = await ctx.send(embed = embed)
        time.sleep(1)
        await msg.add_reaction('✅')
    else:
        embed = discord.Embed(description = f'У вас нет прав для выполнения данной операции', colour=discord.Color.from_rgb(47, 49, 54))
        await ctx.send(embed = embed)

@client.command()
async def reboot(ctx):
    if ctx.author.id == 704649187433644032 or 628999674812170251:
        embed = discord.Embed(description = 'Перезагрузкаᅠбота', colour=discord.Color.from_rgb(47, 49, 54))
        msg = await ctx.send(embed = embed)
        time.sleep(3)
        await msg.add_reaction('✅')
        time.sleep(0)
        os.execv(sys.executable, ["python"] + sys.argv)
    else:
        embed = discord.Embed(description = 'У вас нет прав для выполнения данной операции', colour=discord.Color.from_rgb(47, 49, 54))
        await ctx.send(embed = embed)

@client.command()
async def support(ctx, *, args=None):
    me = client.get_user(319416314966048770)
    embed = discord.Embed(title = f'{ctx.author}({ctx.author.id})', description = args, colour=discord.Color.from_rgb(47, 49, 54))
    embed.set_thumbnail(url=ctx.message.author.avatar_url)
    await ctx.message.delete()
    await me.send(embed = embed)
    emb = discord.Embed(description = f'{ctx.author.mention} ваше сообщение отправлено в службу поддержки. Вам ответят в течении 24 часов.', color = 0xbae4cc)
    await ctx.send(embed = emb)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

if config['antispam_system'] is True:
    client.load_extension("systems.spamsys")
client.load_extension("systems.levelsys")    

# Uses the bot token to login, so don't remove this.
client.run(config['Bot_Token'])

# End Of Main
