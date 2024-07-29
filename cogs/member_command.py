import disnake
import sqlite3
from disnake.ext import commands
from disnake import Localized
from functools import lru_cache


@lru_cache(maxsize=None)
class AdminCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_ex = sqlite3.connect('except_user.db')
        self.cour_ex = self.db_ex.cursor()

    @commands.slash_command(description=Localized(key="CLEAR-COMMAND-DESCRIPTIONS"))
    @commands.default_member_permissions(manage_messages=True)
    async def clear(self, ctx,
                    amount: int = commands.param(description=Localized(key="CLEAR-COMMAND-DESCRIPTIONS_PARAMETERS"))):
        my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=ctx.author.guild.id,
                                       name="системные-сообщения")

        await ctx.response.defer()

        if str(ctx.locale) == "ru":
            emb = disnake.Embed(title=self.bot.i18n.get(key="CLEAR-COMMAND_EMBED-TITLE")["ru"],
                                description=f'{self.bot.i18n.get(key="CLEAR-COMMAND_EMBED-DESCRIPTION")["ru"]} {amount}',
                                colour=disnake.Colour.green())

            await ctx.followup.send(embed=emb, delete_after=20)

        elif str(ctx.locale) == "uk" or str(ctx.locale) ==  "ua":
            emb = disnake.Embed(title=self.bot.i18n.get(key="CLEAR-COMMAND_EMBED-TITLE")["uk"],
                                description=f'{self.bot.i18n.get(key="CLEAR-COMMAND_EMBED-DESCRIPTION")["uk"]} {amount}',
                                colour=disnake.Colour.green())

            await ctx.followup.send(embed=emb, delete_after=20)

        else:
            emb = disnake.Embed(title=self.bot.i18n.get(key="CLEAR-COMMAND_EMBED-TITLE")["en-US"],
                                description=f'{self.bot.i18n.get(key="CLEAR-COMMAND_EMBED-DESCRIPTION")["en-US"]} {amount}',
                                colour=disnake.Colour.green())

            await ctx.followup.send(embed=emb, delete_after=20)

        emb1 = disnake.Embed(title="Внимание",
                             description=f"Пользаватель {ctx.author.global_name} очистил канал: {ctx.channel.mention}",
                             colour=disnake.Colour.yellow())

        emb1.add_field(name="Очищено сообщений", value=f"{amount}")

        await my_channel.send(embed=emb1)
        await ctx.channel.purge(limit=amount)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
