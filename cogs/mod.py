import discord
from discord.ext import commands
from ruamel.yaml import YAML

yaml = YAML()
with open("Configs/config.yml", "r", encoding="utf-8") as file:
    config = yaml.load(file)


class moderation(commands.Cog):
    def __init__(self, client):
        self.client=client


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Загружен ког: {__name__}')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, name_or_id, *, reason=None):
        """unban someone
        Parameters
        • name_or_id - name or id of the banned user
        • reason - reason why the user was unbanned
        """
        ban = await ctx.get_ban(name_or_id)

        try:
            await ctx.guild.unban(ban.user, reason=reason)
        except:
            success = False
        else:
            success = True

        emb = await self.format_mod_embed(ctx, ban.user, success, "unban")

        await ctx.send(embed=emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addrole(self, ctx, member: discord.Member, *, role: discord.Role):
        """Add a role to someone else
        Parameter
        • member - the name or id of the member
        • role - the name or id of the role"""
        if not role:
            embed = discord.Embed(description = 'Данной роли не существует', colour=discord.Color.from_rgb(47, 49, 54))
            await ctx.send(embed = embed)
        await member.add_roles(role)
        
        await ctx.send(embed=discord.Embed(
            description=f'Добавленаᅠроль:ᅠ`{role.name}`',
            colour=discord.Color.from_rgb(47, 49, 54)))       

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removerole(self, ctx, member: discord.Member, *, role: discord.Role):
        """Remove a role from someone else
        Parameter
        • member - the name or id of the member
        • role - the name or id of the role"""
        await member.remove_roles(role)
        await ctx.send(embed=discord.Embed(
            description=f'Убранаᅠроль:ᅠ`{role.name}`',
            colour=discord.Color.from_rgb(47, 49, 54)))   

    @commands.command(description="Очистить чат", usage="=clear <количество>")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await ctx.send(embed=discord.Embed(
            description=f'❗️ Удалено {amount} сообщений.',
            colour=discord.Color.from_rgb(47, 49, 54)),
            delete_after=3)


    @commands.command(aliases=["help mode"])
    async def helpm (self, ctx):
        p = config['Prefix']
        embed = discord.Embed(colour=discord.Color.from_rgb(47, 49, 54), title = "", description = f"`{p}unban 'member id/ping'` - разбанить участника\n`{p}clear 'amount'` - очистить сообщения\n`{p}addrole 'member' 'role'` - дать человеку роль\n`{p}removerole 'member' 'role'` - забрать у человека роль")
        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(moderation(client))