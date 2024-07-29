import disnake
from disnake.ext import commands
from disnake import Localized
from bot import i18n_emb_message


class UserCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.btn_list = ["/help", "/play", "/report"]
        # self.db = sqlite3.connect('warn.db')
        # self.db_ex = sqlite3.connect('except_user.db')
        # self.cour = self.db.cursor()
        # self.cour_ex = self.db_ex.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        # Изменяем статус бота на активный
        activity = disnake.Activity(name="music", type=disnake.ActivityType.listening)
        await self.bot.change_presence(status=disnake.Status.online, activity=activity)
        # Выводим сообщение что бот запущен
        print(f"{self.bot.user} only")

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        print(error)

        if isinstance(error, commands.CommandNotFound):
            emb = disnake.Embed(title='Command not found!',
                                description=f'```{ctx.author.content}``` command enter wrong. '
                                            f'If you forget commands, enter ```/help```', colour=disnake.Colour.red())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar)

            await ctx.send(embed=emb)

    @commands.slash_command(description=Localized(key="REPORT-COMMAND-DESCRIPTIONS"))
    @commands.cooldown(1, 1)
    async def report(self, ctx,
                     message: str = commands.param(
                         description=Localized(key="REPORT-COMMAND-DESCRIPTIONS_PARAMETERS-MESSAGE"))):

        member = disnake.utils.get(self.bot.get_all_members(), id=843213314163081237)

        emb = disnake.Embed(title='Report', description=f'{message}', colour=disnake.Colour.red())

        emb.set_footer(text=f'Report from {ctx.author.global_name}',
                       icon_url=ctx.author.avatar)

        await member.send(embed=emb)

        await i18n_emb_message(ctx, "REPORT-COMMAND_EMBED-TITLE", "REPORT-COMMAND_EMBED-DESCRIPTION",
                               title_extra=":white_check_mark:", colour=disnake.Colour.green(), response=True,
                               ephemeral=True)


def setup(bot):
    bot.add_cog(UserCommand(bot))
