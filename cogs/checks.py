import disnake
import string
import sqlite3
from disnake.ext import commands
from datetime import timedelta, datetime
from functools import lru_cache
from config import ban_words

time_window_milliseconds = 5000
max_msg_per_window = 5
author_msg_times = {}


@lru_cache(maxsize=None)
class UserCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect('warn.db')
        self.cour = self.db.cursor()
        self.link_apply = []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        msg = message.content.lower()

        if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split()} \
                .intersection(set(ban_words)) != set():
            await message.channel.purge(limit=1)

            emb = disnake.Embed(title='Прекрати ругатся!',
                                description='Ты получаеш мут и + предупреждение за нарушение правил сервера',
                                colour=disnake.Colour.yellow())

            emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
            emb.set_footer(text=message.author.name, icon_url=message.author.avatar)

            await message.channel.send(embed=emb)

            self.cour.execute("UPDATE users SET warns = warns + 1 WHERE id = {}".format(message.author.id))
            self.db.commit()

            emb1 = disnake.Embed(title="Зафиксировано нарушение правил",
                                 description=f"Пользавател {message.author.name}#{message.author.discriminator} "
                                             f"нарушил правила сервера",
                                 colour=disnake.Colour.dark_red())

            emb1.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

            emb1.add_field(name='Внимание!',
                           value='@everyone был заметен нарушитель правил', inline=False)
            emb1.add_field(name='Канал нарушения', value=f'{message.channel.mention}')
            emb1.add_field(name='Содержание удалёного Сообщения', value=f'{message.content}')
            emb1.add_field(name='User ID', value=f'{message.author.id}')

            my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=message.author.guild.id,
                                           name="системные-сообщения")

            await my_channel.send(embed=emb1)

            await message.author.timeout(duration=timedelta(minutes=10), reason="Нарушенил правила сервера")

            try:
                emb2 = disnake.Embed(title='Ты получил мут за нарушение правил сервера',
                                     colour=disnake.Colour.yellow())

                emb2.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                await message.author.send(embed=emb2)
                return
            except:
                pass
        for i in ban_words:
            if i in msg:
                await message.channel.purge(limit=1)

                emb = disnake.Embed(title='Прекрати ругатся!',
                                    description='Ты получеш мут и + предупреждение за нарушение правил сервера',
                                    colour=disnake.Colour.yellow())

                emb.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
                emb.set_footer(text=message.author.name, icon_url=message.author.avatar)

                await message.channel.send(embed=emb)

                self.cour.execute("UPDATE users SET warns = warns + 1 WHERE id = {}".format(message.author.id))
                self.db.commit()

                my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=message.author.guild.id,
                                               name="системные-сообщения")

                emb1 = disnake.Embed(title="Зафиксировано нарушение правил",
                                     description=f"Пользавател {message.author.name}#{message.author.discriminator} "
                                                 f"нарушил правила сервера",
                                     colour=disnake.Colour.dark_red())

                emb1.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                emb1.add_field(name='Внимание!',
                               value='@everyone был заметен нарушитель правил', inline=False)
                emb1.add_field(name='Канал нарушения', value=f'{message.channel.mention}')
                emb1.add_field(name='Содержание удалёного Сообщения', value=f'{message.content}')
                emb1.add_field(name='User ID', value=f'{message.author.id}')

                await my_channel.send(embed=emb1)

                await message.author.timeout(duration=timedelta(minutes=10), reason="Нарушенил правила сервера")

                try:
                    emb3 = disnake.Embed(title='Ты получил мут за нарушения правил сервера',
                                         colour=disnake.Colour.yellow())

                    emb3.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                    await message.author.send(embed=emb3)
                    return
                except:
                    pass

        author_id = message.author.id
        # Получение текущого времени в миллисекундах
        curr_time = datetime.now().timestamp() * 1000

        # Создание пустого списка для идентификатора автора, если он не существует
        if not author_msg_times.get(author_id, False):
            author_msg_times[author_id] = []

        author_msg_times[author_id].append(curr_time)

        # Находится начало нашего временного окна.
        expr_time = curr_time - time_window_milliseconds

        # Находим время сообщения, которое произошло до начала нашего окна
        expired_msgs = [
            msg_time for msg_time in author_msg_times[author_id]
            if msg_time < expr_time
        ]

        # Удалить все сообщения с истекшим сроком действия из нашего списка
        for msg_time in expired_msgs:
            author_msg_times[author_id].remove(msg_time)

        if len(author_msg_times[author_id]) > max_msg_per_window:
            await message.delete()
            await message.author.timeout(duration=timedelta(hours=1), reason="Спам")

            self.cour.execute("UPDATE users SET warns = warns + 1 WHERE id = {}".format(message.author.id))
            self.db.commit()

            await message.channel.send(embed=disnake.Embed(title="Прекрати спамить",
                                                           description="Ты получаеш мут на 1 час + варн за спам!",
                                                           colour=disnake.Colour.dark_red()),
                                       delete_after=5)

        if 'https://discord.gg/' in msg:
            if msg in self.link_apply:
                pass
            else:
                await message.channel.purge(limit=1)

                emb = disnake.Embed(title="Нарушаем!",
                                    description="Ты получаеш предупреждение за (возможно) рекламною сылку ")
                emb.add_field(name="Ошибочно ппосчитали что ето сылка на другой сервер?",
                              value="Если так тогда обратитесть к администратору или моему разработчику "
                                    "для добавления ёё в исключение")

                self.cour.execute("UPDATE users SET warns = warns + 1 WHERE id = {}".format(message.author.id))
                self.db.commit()

                await message.channel.send(embed=emb)

        warns = self.cour.execute("SELECT warns FROM users WHERE id = {}".format(message.author.id)).fetchone()[0]

        if warns >= 5:
            self.cour.execute("UPDATE users SET warns = warns - 5 WHERE id = {}".format(message.author.id))
            self.cour.execute("UPDATE users SET count = count + 1 WHERE id = {}".format(message.author.id))
            self.db.commit()

            counter = self.cour.execute("SELECT count FROM users WHERE id = {}".format(message.author.id)).fetchone()[0]

            if counter >= 3:
                self.cour.execute("UPDATE users SET count = count - 3 WHERE id = {}".format(message.author.id))
                self.db.commit()
                link = await message.channel.create_invite(max_age=300)

                emb_ban = disnake.Embed(title="Ты был кикнут из сервера",
                                        description=f"{link}",
                                        colour=disnake.Colour.dark_red())

                emb_ban.add_field(name="Сервер с которого кикнули", value=f'{message.guild.name}')
                emb_ban.add_field(name="Причина мута",
                                  value="Превишение счётчика нарушений")

                await message.author.send(embed=emb_ban)

                await message.author.kick(reason="Превишение счётчика нарушений")
                emb_n = disnake.Embed(title="Пользаватель бил кикнут из серва",
                                      colour=disnake.Colour.dark_red())
                emb_n.add_field(name="Ник пользавателя", value=f"{message.author.name}")
                emb_n.add_field(name="Причина кика", value="Превишение счётчика нарушений")

                await message.channel.send(embed=emb_n)
            else:
                emb_b = disnake.Embed(title="Пользаватель получил мут",
                                      colour=disnake.Colour.dark_red())

                emb_b.add_field(name="Ник пользавателя", value=f"{message.author.name}")
                emb_b.add_field(name="Время мута", value='1 день')
                emb_b.add_field(name="Причина мута", value="Превишение счётчика предупреждений")
                emb_b.add_field(name="*Напоминание*", value="При превишении счетчика предупреждений "
                                                            "будет повишаться счетчик нарушений",
                                inline=False)
                await message.author.timeout(duration=timedelta(days=1), reason="Нарушенил правила сервера")

                await message.channel.send(embed=emb_b)


def setup(bot):
    bot.add_cog(UserCheck(bot))
