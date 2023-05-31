import disnake
from disnake.ext import commands


class OwnerCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="ping", description="Пинг бота")
    @commands.is_owner()
    async def ping_test(self, ctx):
        ping_bot = round(self.bot.latency * 1000)

        await ctx.response.send_message(f'Ping bot: {ping_bot} ms')

    @commands.slash_command(description="Прекращение работы")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.response.send_message('Заканчиваю роботу')
        exit()


def setup(bot):
    bot.add_cog(OwnerCommands(bot))