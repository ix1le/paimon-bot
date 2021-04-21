import discord
from discord.ext import commands

class misc(commands.Cog):
    def __init__(self, client):
        self.client=client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Загружен ког: {__name__}')

    @commands.command()
    async def test(self, ctx):
        emb = discord.Embed(color = 0xFFC300, description = ':warning:')
        await ctx.send(embed = emb) 

def setup(client):
    client.add_cog(misc(client))