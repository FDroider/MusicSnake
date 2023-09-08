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

    @commands.slash_command(name="except", description=Localized(key="EXCEPT-COMMAND-DESCRIPTIONS"),
                            guild_ids=[1087330855913000970, 1089441751053389865])
    @commands.default_member_permissions(administrator=True)
    async def except_user(self, ctx, user: disnake.User = commands.param(description=Localized(key="EXCEPT-COMMAND-DESCRIPTIONS_PARAMETERS"))):
        if self.cour_ex.execute(f"SELECT guild FROM exct WHERE guild = {ctx.author.guild.id}").fetchone() is None and \
                self.cour_ex.execute(f"SELECT user FROM exct WHERE user = {user.id}").fetchone() is None:

            self.cour_ex.execute(f"INSERT INTO exct VALUES ({user.id}, {ctx.author.guild.id})")

            self.db_ex.commit()
            if str(ctx.locale) == "ru":
                emb = disnake.Embed(title=self.bot.i18n.get(key="EXCEPT-COMMAND-SUCCESS_EMBED-TITLE")["ru"],
                                    description=self.bot.i18n.get(key="EXCEPT-COMMAND-SUCCESS_EMBED-DESCRIPTION")["ru"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb, ephemeral=True)

            elif str(ctx.locale) == "uk" or str(ctx.locale) ==  "ua":
                emb = disnake.Embed(title=self.bot.i18n.get(key="EXCEPT-COMMAND-SUCCESS_EMBED-TITLE")["uk"],
                                    description=self.bot.i18n.get(key="EXCEPT-COMMAND-SUCCESS_EMBED-DESCRIPTION")["uk"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb, ephemeral=True)

            else:
                emb = disnake.Embed(title=self.bot.i18n.get(key="EXCEPT-COMMAND-SUCCESS_EMBED-TITLE")["en-US"],
                                    description=self.bot.i18n.get(key="EXCEPT-COMMAND-SUCCESS_EMBED-DESCRIPTION")["en-US"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb, ephemeral=True)

        else:
            if str(ctx.locale) == "ru":
                emb_e = disnake.Embed(title=self.bot.i18n.get(key="EXCEPT-COMMAND-ERROR_EMBED-TITLE")["ru"],
                                      description=self.bot.i18n.get(key="EXCEPT-COMMAND-ERROR_EMBED-DESCRIPTION")["ru"],
                                      colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_e, ephemeral=True)

            elif str(ctx.locale) == "uk" or str(ctx.locale) == "ua":
                emb_e = disnake.Embed(title=self.bot.i18n.get(key="EXCEPT-COMMAND-ERROR_EMBED-TITLE")["uk"],
                                      description=self.bot.i18n.get(key="EXCEPT-COMMAND-ERROR_EMBED-DESCRIPTION")["uk"],
                                      colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_e, ephemeral=True)

            else:
                emb_e = disnake.Embed(title=self.bot.i18n.get(key="EXCEPT-COMMAND-ERROR_EMBED-TITLE")["en-US"],
                                      description=self.bot.i18n.get(key="EXCEPT-COMMAND-ERROR_EMBED-DESCRIPTION")["en-US"],
                                      colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_e, ephemeral=True)

    @commands.slash_command(name="del_except", description=Localized(key="DEL-EXCEPT-COMMAND-DESCRIPTIONS"),
                            guild_ids=[1087330855913000970, 1089441751053389865])
    @commands.default_member_permissions(administrator=True)
    async def del_except_user(self, ctx,
                              user: disnake.User = commands.param(description="DEL-EXCEPT-COMMAND-DESCRIPTIONS_PARAMETERS")):
        if not self.cour_ex.execute(f"SELECT user FROM exct WHERE user = {user.id}").fetchone() is None and \
           not self.cour_ex.execute(f"SELECT guild FROM exct WHERE guild = {ctx.author.guild.id}").fetchone() is None:

            self.cour_ex.execute(f"DELETE FROM exct WHERE user = {user.id}")
            self.cour_ex.execute(f"DELETE FROM exct WHERE guild = {ctx.author.guild.id}")

            self.db_ex.commit()

            if str(ctx.locale) == "ru":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-SUCCESS_EMBED-TITLE")["ru"],
                                    description=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-SUCCESS_EMBED-DESCRIPTION")["ru"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb, ephemeral=True)

            elif str(ctx.locale) == "uk" or str(ctx.locale) == "ua":
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-SUCCESS_EMBED-TITLE")["uk"],
                                    description=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-SUCCESS_EMBED-DESCRIPTION")["uk"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb, ephemeral=True)

            else:
                emb = disnake.Embed(title=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-SUCCESS_EMBED-TITLE")["en-US"],
                                    description=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-SUCCESS_EMBED-DESCRIPTION")["en-US"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb, ephemeral=True)
        else:

            if str(ctx.locale) == "ru":
                emb_e = disnake.Embed(title=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-ERROR_EMBED-TITLE")["ru"],
                                      description=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-ERROR_EMBED-DESCRIPTION")["ru"],
                                      colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_e, ephemeral=True)

            elif str(ctx.locale) == "uk" or str(ctx.locale) == "ua":
                emb_e = disnake.Embed(title=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-ERROR_EMBED-TITLE")["uk"],
                                      description=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-ERROR_EMBED-DESCRIPTION")["uk"],
                                      colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_e, ephemeral=True)

            else:
                emb_e = disnake.Embed(title=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-ERROR_EMBED-TITLE")["en-US"],
                                      description=self.bot.i18n.get(key="DEL-EXCEPT-COMMAND-ERROR_EMBED-DESCRIPTION")["en-US"],
                                      colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_e, ephemeral=True)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
