import disnake
import sqlite3
from disnake.ext import commands
from datetime import timedelta, datetime
from functools import lru_cache


time_window_milliseconds = 5000
max_msg_per_window = 5
author_msg_times = {}


@lru_cache(maxsize=None)
class SpamCheck(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect('warn.db')
        self.db_ex = sqlite3.connect('except_user.db')
        self.cour = self.db.cursor()
        self.cour_ex = self.db_ex.cursor()

    @commands.Cog.listener("on_message")
    async def spam_check(self, message):
        if message.author.bot:
            return

        try:
            ex_user = self.cour_ex.execute(f"SELECT user FROM exct WHERE user = {message.author.id}").fetchone()[0]
            ex_server = self.cour_ex.execute(f"SELECT guild FROM exct WHERE guild = {message.author.guild.id}").fetchone()[0]

            if message.author.id == ex_user and message.author.guild.id == ex_server:
                return
        except:
            pass

        ctx = disnake.CommandInteraction

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
            author_msg = []
            author_msg.append(author_id)

            if len(author_msg) > 4:
                channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=message.author.guild.id,
                                            name="системные-сообщения")

                if str(ctx.locale) == "ru":
                    pass
                elif str(ctx.locale) == "uk":
                    pass
                else:
                    pass

                await channel.send("@everyone Замечена подозрительная активность на сервере! \nВозможно ето рейд!")

            self.cour.execute("UPDATE users SET warns = warns + 1 WHERE id = {}".format(message.author.id))
            self.db.commit()

            my_channel = disnake.utils.get(self.bot.get_all_channels(), guild__id=message.author.guild.id,
                                           name="системные-сообщения")

            try:
                await message.author.timeout(duration=timedelta(hours=1), reason="Спам")

                await message.channel.send(embed=disnake.Embed(title="Прекрати спамить",
                                                               description="Ты получаеш мут на 1 час + варн за спам!",
                                                               colour=disnake.Colour.dark_red()),
                                           delete_after=5)
            except disnake.errors.Forbidden:
                # Содаём Embed для того чтоб уведомить администрацию о нарушителе и о невозможности выдать наказание
                emb1 = disnake.Embed(title="Зафиксировано нарушение правил",
                                     description=f"Пользаватель {message.author.global_name} "
                                                 f"_спамит!_",
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
    bot.add_cog(SpamCheck(bot))
