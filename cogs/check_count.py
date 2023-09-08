import asyncio
import disnake
import sqlite3
from datetime import timedelta
from disnake.ext import commands
from functools import lru_cache


@lru_cache(maxsize=None)
class CountCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect('warn.db')
        self.db_ex = sqlite3.connect('except_user.db')
        self.cour = self.db.cursor()
        self.cour_ex = self.db_ex.cursor()

    @commands.Cog.listener("on_message")
    async def count_check(self, message):
        if message.author.bot:
            return

        warns = self.cour.execute("SELECT warns FROM users WHERE id = {}".format(message.author.id)).fetchone()[0]
        try:
            ex_user = self.cour_ex.execute(f"SELECT user FROM exct WHERE user = {message.author.id}").fetchone()[0]
            ex_server = self.cour_ex.execute(f"SELECT guild FROM exct WHERE guild = {message.author.guild.id}").fetchone()[0]

            if message.author.id == ex_user and message.author.guild.id == ex_server:
                return
        except:
            pass

        if warns >= 2:
            self.cour.execute("UPDATE users SET warns = warns - 2 WHERE id = {}".format(message.author.id))
            self.cour.execute("UPDATE users SET count = count + 1 WHERE id = {}".format(message.author.id))
            self.db.commit()

            counter = self.cour.execute("SELECT count FROM users WHERE id = {}".format(message.author.id)).fetchone()[0]

            await message.author.timeout(duration=timedelta(days=1), reason="Нарушенил правила сервера")

            if counter > 2:
                self.cour.execute("UPDATE users SET count = count - 2 WHERE id = {}".format(message.author.id))
                self.db.commit()
                link = await message.channel.create_invite(max_age=300)
                ctx = disnake.CommandInteraction

                if str(ctx.locale) == "ru":
                    emb_ban = disnake.Embed(title=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED1-TITLE")["ru"],
                                            description=f"{link}",
                                            colour=disnake.Colour.dark_red())

                    emb_ban.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED1-FIELD1-NAME")["ru"],
                                      value=f'{message.guild.name}')
                    emb_ban.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED1-FIELD2-NAME")["ru"],
                                      value=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED1-FIELD2-VALUE")["ru"])

                    await message.author.send(embed=emb_ban)

                    emb_n = disnake.Embed(title=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED2-TITLE")["ru"],
                                          colour=disnake.Colour.dark_red())
                    emb_n.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED2-FIELD1-NAME")["ru"],
                                    value=f"{message.author.global_name}")
                    emb_n.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED2-FIELD2-NAME")["ru"],
                                    value=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED2-FILED2-VALUE")["ru"])

                    await message.channel.send(embed=emb_n)

                    await message.author.ban(reason="Превишение счётчика нарушений")
                    await asyncio.sleep(60 * 60 * 24)
                    await message.author.unban(reason=None)

                    emb_b = disnake.Embed(title=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-TITLE")["ru"],
                                          colour=disnake.Colour.dark_red())

                    emb_b.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD1-NAME")["ru"],
                                    value=f"{message.author.global_name}")
                    emb_b.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD2-NAME")["ru"],
                                    value=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD2-VALUE")["ru"])
                    emb_b.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD3-NAME")["ru"],
                                    value=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD3-VALUE")["ru"])
                    emb_b.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD4-NAME")["ru"],
                                    value=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD4-VALUE")["ru"],
                                    inline=False)

                    await message.channel.send(embed=emb_b)

                    await message.author.ban(reason="Нарушенил правила сервера")
                    await asyncio.sleep(60 * 60 * 24)
                    await message.author.unban(reason=None)

                elif str(ctx.locale) == "uk":
                    emb_ban = disnake.Embed(title=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED1-TITLE")["uk"],
                                            description=f"{link}",
                                            colour=disnake.Colour.dark_red())

                    emb_ban.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED1-FIELD1-NAME")["uk"],
                                      value=f'{message.guild.name}')
                    emb_ban.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED1-FIELD2-NAME")["uk"],
                                      value=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED1-FIELD2-VALUE")["uk"])

                    await message.author.send(embed=emb_ban)

                    emb_n = disnake.Embed(title=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED2-TITLE")["uk"],
                                          colour=disnake.Colour.dark_red())
                    emb_n.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED2-FIELD1-NAME")["uk"],
                                    value=f"{message.author.global_name}")
                    emb_n.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED2-FIELD2-NAME")["uk"],
                                    value=self.bot.i18n.get(key="CHECK-COUNT-BAN_EMBED2-FILED2-VALUE")["uk"])

                    await message.channel.send(embed=emb_n)

                    await message.author.ban(reason="Превишение счётчика нарушений")
                    await asyncio.sleep(60 * 60 * 24)
                    await message.author.unban(reason=None)

                    emb_b = disnake.Embed(title=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-TITLE")["uk"],
                                          colour=disnake.Colour.dark_red())

                    emb_b.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD1-NAME")["uk"],
                                    value=f"{message.author.global_name}")
                    emb_b.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD2-NAME")["uk"],
                                    value=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD2-VALUE")["uk"])
                    emb_b.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD3-NAME")["uk"],
                                    value=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD3-VALUE")["uk"])
                    emb_b.add_field(name=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD4-NAME")["uk"],
                                    value=self.bot.i18n.get(key="CHECK-COUNT-NOTIFICATION_EMBED-FIELD4-VALUE")["uk"],
                                    inline=False)

                    await message.channel.send(embed=emb_b)

                    await message.author.ban(reason="Нарушенил правила сервера")
                    await asyncio.sleep(60 * 60 * 24)
                    await message.author.unban(reason=None)

                else:
                    emb_ban = disnake.Embed(title="Ты был забанен на сервере",
                                            description=f"{link}",
                                            colour=disnake.Colour.dark_red())

                    emb_ban.add_field(name="Сервер на котором забанили", value=f'{message.guild.name}')
                    emb_ban.add_field(name="Причина бана",
                                      value="Превишение счётчика нарушений")

                    await message.author.send(embed=emb_ban)

                    emb_n = disnake.Embed(title="Пользаватель бил забанен",
                                          colour=disnake.Colour.dark_red())
                    emb_n.add_field(name="Ник пользавателя", value=f"{message.author.global_name}")
                    emb_n.add_field(name="Причина кика", value="Превишение счётчика нарушений")

                    await message.channel.send(embed=emb_n)

                    await message.author.ban(reason="Превишение счётчика нарушений")
                    await asyncio.sleep(60*60*24)
                    await message.author.unban(reason=None)

                    emb_b = disnake.Embed(title="Пользаватель получил бан",
                                          colour=disnake.Colour.dark_red())

                    emb_b.add_field(name="Ник пользавателя", value=f"{message.author.global_name}")
                    emb_b.add_field(name="Время бана", value='1 день')
                    emb_b.add_field(name="Причина бана", value="Превишение счётчика предупреждений")
                    emb_b.add_field(name="*Напоминание*", value="При превишении счетчика предупреждений "
                                                                "будет повишаться счетчик нарушений",
                                    inline=False)

                    await message.channel.send(embed=emb_b)

                    await message.author.ban(reason="Нарушенил правила сервера")
                    await asyncio.sleep(60 * 60 * 24)
                    await message.author.unban(reason=None)




def setup(bot):
    bot.add_cog(CountCheck(bot))
