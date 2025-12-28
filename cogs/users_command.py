import disnake
from disnake.ext import commands
from disnake import Localized, ModalInteraction
from bot import i18n_emb_message
from disnake import TextInputStyle

class UserCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.btn_list = ["/help", "/play", "/report"]

    @commands.Cog.listener()
    async def on_ready(self):
        activity = disnake.Activity(name="music", type=disnake.ActivityType.listening)
        await self.bot.change_presence(status=disnake.Status.online, activity=activity)
        print(f"{self.bot.user} only")

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        print(error)

    @commands.slash_command(description=Localized(key="REPORT-COMMAND-DESCRIPTIONS"))
    @commands.cooldown(1, 1)
    async def report(self, ctx,
                     message: str = commands.param(
                         description=Localized(key="REPORT-COMMAND-DESCRIPTIONS_PARAMETERS-MESSAGE"))):
        member = self.bot.get_user(843213314163081237)

        emb = disnake.Embed(title='Report', description=f'{message}', colour=disnake.Colour.red())

        emb.set_footer(text=f'Report from {ctx.author.global_name}',
                       icon_url=ctx.author.avatar)

        await member.send(embed=emb)

        await i18n_emb_message(ctx, "REPORT-COMMAND_EMBED-TITLE", "REPORT-COMMAND_EMBED-DESCRIPTION",
                               title_extra=":white_check_mark:", colour=disnake.Colour.green(), response=True,
                               ephemeral=True)


def setup(bot):
    bot.add_cog(UserCommand(bot))
