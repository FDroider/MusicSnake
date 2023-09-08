import disnake
from disnake.ext import commands
from disnake import Localized

prefix = '/'


class HelpCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description=Localized(key="HELP-COMMAND-DESCRIPTIONS"))
    async def help(self, ctx: disnake.CommandInteraction):
        if str(ctx.locale) == "ru":
            emb = disnake.Embed(title=self.bot.i18n.get(key="HELP-COMMAND_EMBED-TITLE")["ru"], colour=disnake.Colour.light_gray())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)

            emb.add_field(name='{}hello/hi'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED1-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}play'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED2-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}volume'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED3-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}leave'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED4-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}random'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED5-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}chat'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED6-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}report'.format(prefix), value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED7-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}my_warns'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED8-VALUE")["ru"], inline=False)

            await ctx.response.send_message(embed=emb)
        elif str(ctx.locale) == "uk" or str(ctx.locale) == "ua":
            emb = disnake.Embed(title=self.bot.i18n.get(key="HELP-COMMAND_EMBED-TITLE")["uk"],
                                colour=disnake.Colour.light_gray())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)

            emb.add_field(name='{}hello/hi'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED1-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}play'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED2-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}volume'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED3-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}leave'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED4-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}random'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED5-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}chat'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED6-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}report'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED7-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}my_warns'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED8-VALUE")["uk"], inline=False)

            await ctx.response.send_message(embed=emb)
        else:
            emb = disnake.Embed(title=self.bot.i18n.get(key="HELP-COMMAND_EMBED-TITLE")["en-US"],
                                colour=disnake.Colour.light_gray())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)

            emb.add_field(name='{}hello/hi'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED1-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}play'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED2-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}volume'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED3-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}leave'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED4-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}random'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED5-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}chat'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED6-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}report'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED7-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}my_warns'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-COMMAND_EMBED-FILED8-VALUE")["en-US"], inline=False)

            await ctx.response.send_message(embed=emb)

    @commands.slash_command(description=Localized(key="HELP-ADMIN-COMMAND-DESCRIPTIONS"))
    @commands.default_member_permissions(manage_permissions=True, manage_roles=True)
    async def help_admin(self, ctx):

        if str(ctx.locale) == "ru":
            emb = disnake.Embed(title=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-TITLE")["ru"],
                                colour=disnake.Colour.light_gray())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            emb.add_field(name='{}clear'.format(prefix), value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED1-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}warns'.format(prefix), value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED2-VALUE")["ru"],
                          inline=False)

            emb.add_field(name='{}warn_user'.format(prefix), value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED3-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}del_warn'.format(prefix), value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED4-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}except'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED5-VALUE")["ru"],
                          inline=False)
            emb.add_field(name='{}del_except'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED6-VALUE")["ru"], inline=False)

            await ctx.response.send_message(embed=emb)
        elif str(ctx.locale) == "uk" or str(ctx.locale) == "ua":
            emb = disnake.Embed(title=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-TITLE")["uk"],
                                colour=disnake.Colour.light_gray())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            emb.add_field(name='{}clear'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED1-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}warns'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED2-VALUE")["uk"],
                          inline=False)

            emb.add_field(name='{}warn_user'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED3-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}del_warn'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED4-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}except'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED5-VALUE")["uk"],
                          inline=False)
            emb.add_field(name='{}del_except'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED6-VALUE")["uk"], inline=False)

            await ctx.response.send_message(embed=emb)
        else:
            emb = disnake.Embed(title=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-TITLE")["en-US"],
                                colour=disnake.Colour.light_gray())

            emb.set_footer(text=ctx.author.display_name, icon_url=ctx.author.display_avatar)
            emb.add_field(name='{}clear'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED1-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}warns'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED2-VALUE")["en-US"],
                          inline=False)

            emb.add_field(name='{}warn_user'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED3-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}del_warn'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED4-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}except'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED5-VALUE")["en-US"],
                          inline=False)
            emb.add_field(name='{}del_except'.format(prefix),
                          value=self.bot.i18n.get(key="HELP-ADMIN-COMMAND_EMBED-FILED6-VALUE")["en-US"], inline=False)

            await ctx.response.send_message(embed=emb)


def setup(bot):
    bot.add_cog(HelpCommands(bot))
