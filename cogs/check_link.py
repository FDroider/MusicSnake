import disnake
import sqlite3
from disnake.ext import commands
from functools import lru_cache

@lru_cache(maxsize=None)
class LinkCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ctx = disnake.CommandInteraction
        self.db = sqlite3.connect('warn.db')
        self.db_ex = sqlite3.connect('except_user.db')
        self.cour = self.db.cursor()
        self.cour_ex = self.db_ex.cursor()
        self.link_apply = []

    @staticmethod
    def get_locale(member):
        return member.locale

    @commands.Cog.listener("on_message")
    async def link_check(self, message: disnake.Message):
        if message.author.bot:
            return

        try:
            ex_user = self.cour_ex.execute(f"SELECT user FROM exct WHERE user = {message.author.id}").fetchone()[0]
            ex_server = self.cour_ex.execute(f"SELECT guild FROM exct WHERE guild = {message.author.guild.id}").fetchone()[0]

            if message.author.id == ex_user and message.author.guild.id == ex_server:
                return
        except:
            pass

        if message.content.lower() not in self.link_apply:
            if 'https://discord.gg/' in message.content.lower():
                async for links in message.author.guild.audit_logs():

                    if links.action == disnake.AuditLogAction.invite_create:

                        if str(links.target) in message.content:
                            return
                    else:
                        await message.channel.purge(limit=1)

                        if str(self.ctx.locale) == "ru":

                            emb = disnake.Embed(title=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-TITLE")["ru"]}',
                                                description=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-DESCRIPTION")["ru"]}',
                                                colour=disnake.Colour.red())
                            emb.add_field(name=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-FIELD-NAME")["ru"]}',
                                          value=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-FIELD-VALUE")["ru"]}')

                            await message.channel.send(embed=emb)

                        elif str(self.ctx.locale) == "uk":

                            emb = disnake.Embed(title=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-TITLE")["uk"]}',
                                                description=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-DESCRIPTION")["uk"]}',
                                                colour=disnake.Colour.red())
                            emb.add_field(name=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-FIELD-NAME")["uk"]}',
                                          value=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-FIELD-VALUE")["uk"]}')

                            await message.channel.send(embed=emb)
                        else:
                            emb = disnake.Embed(title=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-TITLE")["ru"]}',
                                                description=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-DESCRIPTION")["ru"]}',
                                                colour=disnake.Colour.red())
                            emb.add_field(name=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-FIELD-NAME")["ru"]}',
                                          value=f'{self.bot.i18n.get(key="CHECK-LINK_EMBED-FIELD-VALUE")["ru"]}')
                            await message.channel.send(embed=emb)

                        self.cour.execute("UPDATE users SET warns = warns + 1 WHERE id = {}".format(message.author.id))
                        self.db.commit()

                        break

def setup(bot):
    bot.add_cog(LinkCheck(bot))
