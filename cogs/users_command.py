import disnake
from disnake.ext import commands
from disnake import Localized, ModalInteraction
from bot import i18n_emb_message
from disnake import TextInputStyle

class ModelVote(disnake.ui.Modal):
    def __init__(self, bot: commands.Bot, error):
        self.bot = bot
        self.error_message = error
        components = [
            disnake.ui.TextInput(
                label="Why appear error?",
                placeholder="Enter what to do before appear error",
                custom_id="question",
                style=TextInputStyle.long,
                max_length=3000
            )
        ]
        super().__init__(
            title="Bug report",
            components=components,
        )

    async def callback(self, inter: ModalInteraction, /):
        emb = disnake.Embed(title='Bug report', description=None, colour=disnake.Colour.red())

        emb.add_field(name="Error code", value=f"```{self.error_message}```")

        emb.set_footer(text=f'Report from {inter.author.global_name}',
                       icon_url=inter.author.avatar)
        message = []
        for v in inter.text_values.values():
            message.append(v)
        emb.description = " ".join(message)
        member = self.bot.get_user(843213314163081237)
        await member.send(embed=emb)
        await i18n_emb_message(inter, "REPORT-COMMAND_EMBED-TITLE", "REPORT-COMMAND_EMBED-DESCRIPTION",
                               title_extra=":white_check_mark:", colour=disnake.Colour.green(), response=True,
                               ephemeral=True)

class UserCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.btn_list = ["/help", "/play", "/report"]

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
        view = disnake.ui.View()
        btn_send = disnake.ui.Button(label="Send bug report")

        async def callback(ctx):
            await ctx.response.send_modal(modal=ModelVote(self.bot, error))
            await self.bot.wait_until_ready()

        btn_send.callback = callback

        view.add_item(btn_send)

        emb = disnake.Embed(title='Error',
                            description=f'Error message:\n```{error}```', colour=disnake.Colour.red())

        emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar)

        await ctx.send(embed=emb, ephemeral=True, view=view)

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
