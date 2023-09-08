import random
import disnake
from disnake import Localized
from disnake.ext import commands


class UserCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="random", description=Localized(key="RANDOM-COMMAND-DESCRIPTIONS"))
    async def rand(self, ctx: disnake.CommandInteraction,
                   amount1: int = commands.param(description=Localized(key="RANDOM-COMMAND-DESCRIPTIONS_PARAMETERS-AMOUNT1")),
                   amount2: int = commands.param(description=Localized(key="RANDOM-COMMAND-DESCRIPTIONS_PARAMETERS-AMOUNT2"))):

        random_number = random.randint(amount1, amount2)

        if str(ctx.locale) == "ru":
            emb = disnake.Embed(
                title=f'{self.bot.i18n.get(key="RANDOM-COMMAND_EMBED-TITLE")["ru"]} {random.randint(amount1, amount2)}',
                colour=disnake.Colour.green())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)

            await ctx.response.send_message(embed=emb)
        elif str(ctx.locale) == "uk" or str(ctx.locale) ==  "ua":
            emb = disnake.Embed(
                title=f'{self.bot.i18n.get(key="RANDOM-COMMAND_EMBED-TITLE")["uk"]} {random.randint(amount1, amount2)}',
                colour=disnake.Colour.green())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)

            await ctx.response.send_message(embed=emb)
        else:
            emb = disnake.Embed(
                title=f'{self.bot.i18n.get(key="RANDOM-COMMAND_EMBED-TITLE")["en-US"]} {random.randint(amount1, amount2)}',
                colour=disnake.Colour.green())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)

            await ctx.response.send_message(embed=emb)



def setup(bot):
    bot.add_cog(UserCommands(bot))