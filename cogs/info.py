import discord
from discord.ext import commands


class info(commands.Cog):
    def __init__(self, client):
        self.client=client


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Загружен ког: {__name__}')

    @commands.command(aliases=['server'])
    async def serverinfo(self, ctx, guild: discord.Guild = None):
        embed = discord.Embed(title = f'Информация о сервере {ctx.guild.name}', color = 0x2F3136)
        embed.add_field(name = 'Создатель сервера', value = ctx.guild.owner)
        embed.add_field(name = 'ID севрера', value = ctx.guild.id)
        embed.add_field(name = 'Описание сервера', value = ctx.guild.description)
        embed.add_field(name = 'Кол-во ролей', value = len(ctx.guild.roles))
        embed.add_field(name = 'Кол-во участников', value = ctx.guild.member_count)
        embed.add_field(name = 'Кол-во бустов', value = ctx.guild.premium_subscription_count)
        embed.add_field(name = 'Дата создания сервера', value = ctx.guild.created_at.strftime("%d.%m.%Y \n%H:%M:%S"))
        embed.set_thumbnail(url = ctx.guild.icon_url)
        await ctx.send(embed=embed) 

    @commands.command(aliases=['user'])
    async def userinfo(self, ctx, member: discord.Member):
        roles = member.roles
        role_list = ""
        for role in roles:
            role_list += f"<@&{role.id}> "
        emb = discord.Embed(
            title=f'Информация о пользователе {member}', color = 0x2F3136)
        emb.set_thumbnail(url=member.avatar_url)
        emb.add_field(name='ID', value=member.id)
        emb.add_field(name='Имя', value=member.name)
        # emb.add_field(name='Высшая роль', value=member.top_role)
        emb.add_field(name='Дискриминатор', value=member.discriminator)
        emb.add_field(name='Присоединился к серверу',
                  value=member.joined_at.strftime('%d.%m.%Y \n %H:%M:%S'))
        emb.add_field(name="Присоединился к Discord'y",
                  value=member.created_at.strftime("%d.%m.%Y \n%H:%M:%S"))
        # emb.add_field(name='Роли', value=role_list)
        await ctx.send(embed=emb)

def setup(client):
    client.add_cog(info(client))