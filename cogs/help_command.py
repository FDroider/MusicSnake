import disnake
from disnake.ext import commands
from disnake import Localized

prefix = '/'


class HelpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description=Localized(key="HELP-COMMAND-DESCRIPTIONS"))
    async def help(self, ctx: disnake.CommandInteraction):
        local_user = str(ctx.locale)
        if local_user not in ("ru", "uk", "en-US"):
            local_user= "en-US"

        emb = disnake.Embed(title=self.bot.i18n.get(key="HELP-COMMAND_EMBED-TITLE")[local_user], colour=disnake.Colour.light_gray())

        emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)

        emb.add_field(name='{}play'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED2-VALUE")[local_user],
                      inline=False)
        emb.add_field(name='{}random'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED5-VALUE")[local_user],
                      inline=False)
        emb.add_field(name='{}report'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED7-VALUE")[local_user],
                      inline=False)

        await ctx.response.send_message(embed=emb)


def setup(bot):
    bot.add_cog(HelpCommands(bot))
