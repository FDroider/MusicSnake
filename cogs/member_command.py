import disnake
import sqlite3
from disnake.ext import commands
from disnake import Localized
from bot import i18n_emb_message


class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_ex = sqlite3.connect('except_user.db')
        self.cour_ex = self.db_ex.cursor()

    @commands.slash_command(description=Localized(key="CLEAR-COMMAND-DESCRIPTIONS"))
    @commands.default_member_permissions(manage_messages=True)
    async def clear(self, ctx,
                    amount: int = commands.param(description=Localized(key="CLEAR-COMMAND-DESCRIPTIONS_PARAMETERS"))):

        await ctx.response.defer()

        await ctx.channel.purge(limit=amount)

        await i18n_emb_message(ctx, "CLEAR-COMMAND_EMBED-TITLE", "CLEAR-COMMAND_EMBED-DESCRIPTION",
                               desc_extra=amount, colour=disnake.Colour.green(), delete_after=10)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
