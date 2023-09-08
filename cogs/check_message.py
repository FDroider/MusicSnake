import disnake
import string
import sqlite3
from disnake.ext import commands
from datetime import timedelta
from functools import lru_cache
from config import ban_words


@lru_cache(maxsize=None)
class UserCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect('warn.db')
        self.db_ex = sqlite3.connect('except_user.db')
        self.cour = self.db.cursor()
        self.cour_ex = self.db_ex.cursor()

    @commands.Cog.listener()
    async def on_message(self, message):
        # Проверяем написал ли ето сообщение бот
        if message.author.bot:
            return

        try:
            ex_user = self.cour_ex.execute(f"SELECT user FROM exct WHERE user = {message.author.id}").fetchone()[0]
            ex_server = self.cour_ex.execute(f"SELECT guild FROM exct WHERE guild = {message.author.guild.id}").fetchone()[0]

            if message.author.id == ex_user and message.author.guild.id == ex_server:
                return
        except:
            pass

        # Для удобства переводим весь получений текст в нижний регистр
        msg = message.content.lower()
        ctx = disnake.CommandInteraction

        # Проверяем сообшение на ban_words методом удаления знаков пунктуации
        if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.content.split()} \
                .intersection(set(ban_words)) != set():
            # Удаляем собщение с канала
            await message.channel.purge(limit=1)

            if str(ctx.locale) == "ru":
                pass
            elif str(ctx.locale) == "uk":
                pass
            else:
                pass

            # Создаём Embed чтоб уведомить пользавателя о нарушении
            emb = disnake.Embed(title="Зафиксировано нарушение правил",
                                description='Ты получаешь мут и + предупреждение за нарушение правил сервера',
                                colour=disnake.Colour.yellow())

            # Отправляем сообщение с Embed в канал
            await message.channel.send(embed=emb)

            # В базе данных ищем пользавателя с помощю его id и добавляем ему предупреждение
            self.cour.execute("UPDATE users SET warns = warns + 1 WHERE id = {}".format(message.author.id))
            self.db.commit()

            # Получаем канал под название "системные-сообщения" и сервер на котором находиться сам пользаватель
            my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=message.author.guild.id,
                                           name="системные-сообщения")

            try:
                # Выдаём мут заа нарушения правил
                await message.author.timeout(duration=timedelta(minutes=10), reason="Нарушенил правила сервера")

                # Содаём Embed для того чтоб уведомить администрацию о нарушителе
                emb1 = disnake.Embed(title="Зафиксировано нарушение правил",
                                     description=f"Пользаватель {message.author.global_name} нарушил правила сервера",
                                     colour=disnake.Colour.dark_red())

                emb1.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                emb1.add_field(name='Внимание!', value=' был замечен нарушитель правил', inline=False)
                emb1.add_field(name='Канал нарушения', value=f'{message.channel.mention}')
                emb1.add_field(name='Содержание удалёного сообщения', value=f'{message.content}')
                emb1.add_field(name='User ID', value=f'{message.author.id}')
                emb1.add_field(name="Статус наказания", value="Выданно")

                # Отправляем Embed в канал каторий ми получили в переменной my_channel
                await my_channel.send(embed=emb1)

                # Содаём Embed для уведовленя пользавателя о нарушении
                emb2 = disnake.Embed(title='Ты получил мут за нарушение правил сервера',
                                     colour=disnake.Colour.yellow())

                emb2.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                # Отправка сообщения пользавателю в ЛС
                await message.author.send(embed=emb2)
                return
            # Пишем инструкции на случай если будут какието проблеми с правами
            except disnake.errors.Forbidden:
                # Содаём Embed для того чтоб уведомить администрацию о нарушителе и о невозможности выдать наказание
                emb1 = disnake.Embed(title="Зафиксировано нарушение правил",
                                     description=f"Пользаватель {message.author.global_name} "
                                                 f"нарушил правила сервера",
                                     colour=disnake.Colour.dark_red())

                emb1.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                emb1.add_field(name='Внимание!',
                               value='@everyone был замечен нарушитель правил', inline=False)
                emb1.add_field(name='Канал нарушения', value=f'{message.channel.mention}')
                emb1.add_field(name='Содержание удалёного сообщения', value=f'{message.content}')
                emb1.add_field(name='User ID', value=f'{message.author.id}')
                emb1.add_field(name="Статус наказания", value="Не выданно(Недостаточно прав)")

                # Отправляем Embed в канал каторий ми получили в переменной my_channel
                await my_channel.send(embed=emb1)
                # Вызываем исключение PermissionError
                raise PermissionError

        # Перебераем слова из листа ban_words
        for i in ban_words:
            # Проверяем сообщение на схождение слов пользавателя со словами из ban_words
            if i in msg:
                # Удаляем собщение с канала
                await message.channel.purge(limit=1)

                # Создаём Embed чтоб уведомить пользавателя о нарушении
                emb = disnake.Embed(title='Прекрати ругатся!',
                                    description='Ты получаешь мут и + предупреждение за нарушение правил сервера',
                                    colour=disnake.Colour.yellow())

                # Отправляем сообщение с Embed в канал
                await message.channel.send(embed=emb)

                # В базе данных ищем пользавателя с помощю его id и добавляем ему предупреждение
                self.cour.execute("UPDATE users SET warns = warns + 1 WHERE id = {}".format(message.author.id))
                self.db.commit()

                # Получаем канал под название "системные-сообщения" и сервер на котором находиться сам пользаватель
                my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=message.author.guild.id,
                                               name="системные-сообщения")

                try:
                    # Выдаём мут заа нарушения правил
                    await message.author.timeout(duration=timedelta(minutes=10), reason="Нарушенил правила сервера")

                    # Содаём Embed для того чтоб уведомить администрацию о нарушителе
                    emb1 = disnake.Embed(title="Зафиксировано нарушение правил",
                                         description=f"Пользавател {message.author.global_name} нарушил правила сервера",
                                         colour=disnake.Colour.dark_red())

                    emb1.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                    emb1.add_field(name='Внимание!', value=' был заметен нарушитель правил', inline=False)
                    emb1.add_field(name='Канал нарушения', value=f'{message.channel.mention}')
                    emb1.add_field(name='Содержание удалёного Сообщения', value=f'{message.content}')
                    emb1.add_field(name='User ID', value=f'{message.author.id}')
                    emb1.add_field(name="Статус наказания", value="Выданно")

                    # Отправляем Embed в канал каторий ми получили в переменной my_channel
                    await my_channel.send(embed=emb1)

                    # Содаём Embed для уведовленя пользавателя о нарушении
                    emb3 = disnake.Embed(title='Ты получил мут за нарушения правил сервера',
                                         colour=disnake.Colour.yellow())

                    emb3.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                    # Отправка сообщения пользавателю в ЛС
                    await message.author.send(embed=emb3)
                    return
                # Пишем инструкции на случай если будут какието проблеми с правами
                except disnake.errors.Forbidden:
                    # Содаём Embed для того чтоб уведомить администрацию о нарушителе и о невозможности выдать наказание
                    emb1 = disnake.Embed(title="Зафиксировано нарушение правил",
                                         description=f"Пользаватель {message.author.global_name} "
                                                     f"нарушил правила сервера",
                                         colour=disnake.Colour.dark_red())

                    emb1.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)

                    emb1.add_field(name='Внимание!',
                                   value='@everyone был замечен нарушитель правил', inline=False)
                    emb1.add_field(name='Канал нарушения', value=f'{message.channel.mention}')
                    emb1.add_field(name='Содержание удалёного сообщения', value=f'{message.content}')
                    emb1.add_field(name='User ID', value=f'{message.author.id}')
                    emb1.add_field(name="Статус наказания", value="Не выданно(Недостаточно прав)")

                    # Отправляем Embed в канал каторий ми получили в переменной my_channel
                    await my_channel.send(embed=emb1)
                    # Вызываем исключение PermissionError
                    raise PermissionError


def setup(bot):
    bot.add_cog(UserCheck(bot))
