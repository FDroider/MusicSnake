import random
import disnake
from disnake.ext import commands


class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="random", description="Рандомайзер")
    async def rand(self, inter, amount1: int, amount2: int):
        """
        Parameters
        ----------
        amount1: Первое число
        amount2: Второе число
        """
        emb = disnake.Embed(title=f'Згенерированое число: {random.randint(amount1, amount2)}',
                            colour=disnake.Colour.green())

        emb.set_footer(text=inter.author.name, icon_url=inter.author.avatar)

        await inter.response.send_message(embed=emb)


def setup(bot):
    bot.add_cog(UserCommands(bot))