import disnake
from disnake.ext import commands
from functools import lru_cache


@lru_cache(maxsize=None)
class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Команда для очистки чата")
    @commands.default_member_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """
        Parameters
        ----------
        amount: Количество сообщений
        """
        await ctx.channel.purge(limit=amount)

        await ctx.response.defer()

        emb = disnake.Embed(title='Очищено',
                            description=f'Сообщений очищено: {amount}',
                            colour=disnake.Colour.green())

        await ctx.followup.send(embed=emb, delete_after=20)

        my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=ctx.author.guild.id,
                                       name="системные-сообщения")

        emb1 = disnake.Embed(title="Внимание",
                             description=f"Пользавател {ctx.author.name} очистил канал: {ctx.channel.mention}",
                             colour=disnake.Colour.yellow())

        emb1.add_field(name="Очищено сообщений", value=f"{amount}")

        await my_channel.send(embed=emb1)

        # print(f'[Log] Cleared channel name: {ctx.channel.name}, user: {ctx.author.name}')


def setup(bot):
    bot.add_cog(AdminCommands(bot))
