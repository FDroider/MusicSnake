import random
import disnake
from disnake import Localized
from disnake.ext import commands
from bot import i18n_emb_message


class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="random", description=Localized(key="RANDOM-COMMAND-DESCRIPTIONS"))
    async def rand(self, ctx: disnake.CommandInteraction,
                   amount1: int = commands.param(description=Localized(key="RANDOM-COMMAND-DESCRIPTIONS_PARAMETERS-AMOUNT1")),
                   amount2: int = commands.param(description=Localized(key="RANDOM-COMMAND-DESCRIPTIONS_PARAMETERS-AMOUNT2"))):

        random_number = random.randint(amount1, amount2)

        await i18n_emb_message(ctx, "RANDOM-COMMAND_EMBED-TITLE", False, title_extra={random_number},
                               colour=disnake.Colour.green())



def setup(bot):
    bot.add_cog(UserCommands(bot))