import asyncio
import disnake
from disnake.ext import commands
from disnake import Localized
from asyncio import sleep
from typing import Optional
from functools import lru_cache
import yt_dlp as youtube_dl

linked_allowed = ["https://www.youtube.com/", "https://youtu.be/", "http://youtu.be/", "https://youtube.com/",
                  "https://m.youtube.com/", "http://m.youtube.com/"]

list_of_songs = []
author_play_list = []
author_name_list = []

class ControlPanel(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = Optional[bool]

    def user_locale(self, ctx):
        return str(ctx.locale)

    @disnake.ui.button(label="Pause", style=disnake.ButtonStyle.primary, row=1)
    async def pause(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if self.user_locale(ctx) == "ru":
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Ошибка",
                                          description="Вы не подключены к войс чату",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Ошибка",
                                          description=f"Сейчас руководит парадом пользаватель {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return
        elif self.user_locale(ctx) == "uk" or self.user_locale(ctx) == "ua":
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Помилка",
                                          description="Ви не можете керувати програвачем поки не пыдключены до войс каналу",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Помилка",
                                          description=f"Зараз ботом користується інший учасник сервера: {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return
        else:
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Error",
                                          description="You are not connected to voice chat",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Error",
                                          description=f"Another server member is currently using the bot: {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return

        if self.user_locale(ctx) == "ru":
            if vc.is_playing():
                vc.pause()
                await ctx.send("Пауза", delete_after=5, ephemeral=True)
            else:
                emb = disnake.Embed(description="Музыка уже не воспроизводится или закончилась",
                                    colour=disnake.Colour.brand_red())
                await ctx.response.send_message(embed=emb, delete_after=5, ephemeral=True)

        elif self.user_locale(ctx) == "uk" or self.user_locale(ctx) == "ua":
            if vc.is_playing():
                vc.pause()
                await ctx.send("Пауза", delete_after=5, ephemeral=True)
            else:
                emb = disnake.Embed(description="Музика вже не програється чи закінчилася",
                                    colour=disnake.Colour.brand_red())
                await ctx.response.send_message(embed=emb, delete_after=5, ephemeral=True)

        else:
            if vc.is_playing():
                vc.pause()
                await ctx.send("Pause", delete_after=5, ephemeral=True)
            else:
                emb = disnake.Embed(description="Music is no longer playing or has ended",
                                    colour=disnake.Colour.brand_red())
                await ctx.response.send_message(embed=emb, delete_after=5, ephemeral=True)

        self.value = True

    @disnake.ui.button(label="Resume", style=disnake.ButtonStyle.green, row=1)
    async def resume(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if self.user_locale(ctx) == "ru":
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Ошибка",
                                          description="Вы не подключены к войс чату",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Ошибка",
                                          description=f"Сейчас руководит парадом пользаватель {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return
        elif self.user_locale(ctx) == "uk" or self.user_locale(ctx) == "ua":
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Помилка",
                                          description="Ви не можете керувати програвачем поки не пыдключены до войс каналу",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Помилка",
                                          description=f"Зараз ботом користується інший учасник сервера: {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return
        else:
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Error",
                                          description="You are not connected to voice chat",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Error",
                                          description=f"Another server member is currently using the bot: {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return

        if self.user_locale(ctx) == "ru":
            if vc.is_paused():
                vc.resume()

                await ctx.send("Продолжаю проыгривать", delete_after=5, ephemeral=True)
            else:
                emb = disnake.Embed(description="Музыка уже воспроизводтся",
                                    colour=disnake.Colour.brand_red())

                await ctx.response.send_message(embed=emb, delete_after=5, ephemeral=True)
        elif self.user_locale(ctx) == "uk" or self.user_locale(ctx) == "ua":
            if vc.is_paused():
                vc.resume()

                await ctx.send("Продовжую програвати музику", delete_after=5, ephemeral=True)
            else:
                emb = disnake.Embed(description="Музика вже програвається",
                                    colour=disnake.Colour.brand_red())

                await ctx.response.send_message(embed=emb, delete_after=5, ephemeral=True)

        else:
            if vc.is_paused():
                vc.resume()

                await ctx.send("Continue playing", delete_after=5, ephemeral=True)
            else:
                emb = disnake.Embed(description="Music is already playing",
                                    colour=disnake.Colour.brand_red())

                await ctx.response.send_message(embed=emb, delete_after=5, ephemeral=True)

        self.value = True

    @disnake.ui.button(label="Skip", style=disnake.ButtonStyle.red, row=2)
    async def skip(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if self.user_locale(ctx) == "ru":
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Ошибка",
                                          description="Вы не подключены к войс чату",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Ошибка",
                                          description=f"Сейчас руководит парадом пользаватель {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return
        elif self.user_locale(ctx) == "uk" or self.user_locale(ctx) == "ua":
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Помилка",
                                          description="Ви не можете керувати програвачем поки не пыдключены до войс каналу",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Помилка",
                                          description=f"Зараз ботом користується інший учасник сервера: {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return
        else:
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Error",
                                          description="You are not connected to voice chat",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Error",
                                          description=f"Another server member is currently using the bot: {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return

        if self.user_locale(ctx) == "ru":
            if len(list_of_songs) <= 1:

                emb_e = disnake.Embed(title="Ошибка",
                                      description="Нет следующего видео в очереди", colour=disnake.Colour.red())

                await ctx.send(embed=emb_e, ephemeral=True)
            elif vc.is_playing():
                vc.stop()
                await ctx.send("Загружаю следующее видео")
            elif vc.is_paused():
                vc.stop()
                await ctx.send("Загружаю следующее видео")

        elif self.user_locale(ctx) == "uk" or self.user_locale(ctx) == "ua":
            if len(list_of_songs) <= 1:

                emb_e = disnake.Embed(title="Помилка",
                                      description="Неиає наступної музики в черзі", colour=disnake.Colour.red())

                await ctx.send(embed=emb_e, ephemeral=True)
            elif vc.is_playing():
                vc.stop()
                await ctx.send("Завантажую наступну музику")
            elif vc.is_paused():
                vc.stop()
                await ctx.send("Завантажую наступну музику")

        else:
            if len(list_of_songs) <= 1:

                emb_e = disnake.Embed(title="Error",
                                      description="No next music in queue", colour=disnake.Colour.red())

                await ctx.send(embed=emb_e, ephemeral=True)
            elif vc.is_playing():
                vc.stop()
                await ctx.send("Uploading the next music")
            elif vc.is_paused():
                vc.stop()
                await ctx.send("Uploading the next music")

        self.value = True

    @disnake.ui.button(label="Stop", style=disnake.ButtonStyle.red, row=2)
    async def stop(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if self.user_locale(ctx) == "ru":
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Ошибка",
                                          description="Вы не подключены к войс чату",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Ошибка",
                                          description=f"Сейчас руководит парадом пользаватель {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return
        elif self.user_locale(ctx) == "uk" or self.user_locale(ctx) == "ua":
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Помилка",
                                          description="Ви не можете керувати програвачем поки не пыдключены до войс каналу",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Помилка",
                                          description=f"Зараз ботом користується інший учасник сервера: {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return
        else:
            if ctx.user.voice is None:
                emb_error = disnake.Embed(title="Error",
                                          description="You are not connected to voice chat",
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

                return

            if ctx.author.id != 843213314163081237:
                if author_play_list[0] != ctx.author.id:
                    emb_e = disnake.Embed(title="Error",
                                          description=f"Another server member is currently using the bot: {author_name_list[0]}",
                                          colour=disnake.Colour.red())

                    await ctx.send(embed=emb_e, ephemeral=True)

                    return

        if self.user_locale(ctx) == "ru":
            if vc.is_playing():
                list_of_songs.clear()
                author_play_list.clear()
                author_name_list.clear()
                vc.stop()

                await ctx.send("Воспроизведение прекращено", delete_after=5)

            elif vc.is_paused():
                list_of_songs.clear()
                author_play_list.clear()
                author_name_list.clear()
                vc.stop()

                await ctx.send("Воспроизведение прекращено", delete_after=5)

        elif self.user_locale(ctx) == "uk" or self.user_locale(ctx) == "ua":
            if vc.is_playing():
                list_of_songs.clear()
                author_play_list.clear()
                author_name_list.clear()
                vc.stop()

                await ctx.send("Програвання перервано", delete_after=5)

            elif vc.is_paused():
                list_of_songs.clear()
                author_play_list.clear()
                author_name_list.clear()
                vc.stop()

                await ctx.send("Програвання перервано", delete_after=5)

        else:
            if vc.is_playing():
                list_of_songs.clear()
                author_play_list.clear()
                author_name_list.clear()
                vc.stop()

                await ctx.send("Playback stopped", delete_after=5)

            elif vc.is_paused():
                list_of_songs.clear()
                author_play_list.clear()
                author_name_list.clear()
                vc.stop()

                await ctx.send("Playback stopped", delete_after=5)

        self.value = True


@lru_cache(maxsize=None)
class MusicCommands(commands.Cog):
    bot = commands.Bot
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                               "options": "-vn"}

    # Функция проверки пожжержки
    @staticmethod
    def check_link(url):
        for i in linked_allowed:
            if url.startswith(i):
                return True
            elif url.startswith("https://youtu.be/") or url.startswith("http://youtu.be/"):
                return True
            else:
                return False

    @commands.slash_command(description=Localized(key="PLAY-COMMAND-DESCRIPTIONS"))
    async def play(self, ctx,
                   url: str = commands.param(description=Localized(key="PLAY-COMMAND-DESCRIPTIONS_PARAMETERS"))):
        await ctx.response.defer()

        local_user = str(ctx.locale)

        # Проверка что пользаватель находится в войс чате
        if ctx.user.voice is None:
            if local_user == "ru":
                emb_vice_error = disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-VOICE-ERROR_EMBED-TITLE")["ru"],
                                               description=self.bot.i18n.get(key="PLAY-COMMAND-VOICE-ERROR_EMBED-DESCRIPTION")["ru"],
                                               colour=disnake.Colour.red())

                await ctx.followup.send(embed=emb_vice_error)

            elif local_user == "uk" or local_user == "ua":
                emb_vice_error = disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-VOICE-ERROR_EMBED-TITLE")["uk"],
                                               description=self.bot.i18n.get(key="PLAY-COMMAND-VOICE-ERROR_EMBED-DESCRIPTION")["uk"],
                                               colour=disnake.Colour.red())

                await ctx.followup.send(embed=emb_vice_error)

            else:
                emb_vice_error = disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-VOICE-ERROR_EMBED-TITLE")["en-US"],
                                               description=self.bot.i18n.get(key="PLAY-COMMAND-VOICE-ERROR_EMBED-DESCRIPTION")["en-US"],
                                               colour=disnake.Colour.red())

                await ctx.followup.send(embed=emb_vice_error)
            return

        # Проверяем на поддержку силку на виде
        if self.check_link(url) is False:
            if local_user == "ru":
                emb_sup_error = disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-SUPPORT-ERROR_EMBED-TITLE")["ru"],
                                              description=self.bot.i18n.get(key="PLAY-COMMAND-SUPPORT-ERROR_EMBED-DESCRIPTION")["ru"],
                                              colour=disnake.Colour.red())

                await ctx.followup.send(embed=emb_sup_error)

            elif local_user == "uk" or local_user == "ua":
                emb_sup_error = disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-SUPPORT-ERROR_EMBED-TITLE")["uk"],
                                              description=
                                              self.bot.i18n.get(key="PLAY-COMMAND-SUPPORT-ERROR_EMBED-DESCRIPTION")["uk"],
                                              colour=disnake.Colour.red())

                await ctx.followup.send(embed=emb_sup_error)

            else:
                emb_sup_error = disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-SUPPORT-ERROR_EMBED-TITLE")["en-US"],
                                              description=self.bot.i18n.get(key="PLAY-COMMAND-SUPPORT-ERROR_EMBED-DESCRIPTION")["en-US"],
                                              colour=disnake.Colour.red())

                await ctx.followup.send(embed=emb_sup_error)
            return

        # Подсойдинение к войс чату
        try:
            await ctx.user.voice.channel.connect()

            list_of_songs.append(url)
            author_play_list.append(ctx.author.id)
            author_name_list.append(ctx.author.display_name)
        except:
            print("[Log] Уже подключен или не удалось подключиться")

            list_of_songs.append(url)
            author_play_list.append(ctx.author.id)
            author_name_list.append(ctx.author.display_name)

            await ctx.send("Добавлено в очередь", delete_after=2)

        while len(list_of_songs) > 0:

            if len(list_of_songs) > 1:
                return

            with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(list_of_songs[0], download=False)  # Загрузка видео без скачки

            # URL = ydl.sanitize_info(info)
            URL = info['url']  # Получение информации о url

            source = disnake.FFmpegPCMAudio(URL, executable="ffmpegs/ffmpeg.exe", **self.FFMPEG_OPTIONS)
            vc = ctx.guild.voice_client
            vc.play(source)  # Прогиеривание музыки

            if local_user == "ru":
                msg = await ctx.followup.send(embed=disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-TITLE")["ru"],
                                                                  description=f'{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART1")["ru"]} {info["title"]}\n'
                                                                              f'{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART2")["ru"]} '
                                                                              f'{author_name_list[0]}',
                                                                  colour=disnake.Colour.brand_green()),
                                              view=ControlPanel())

            elif local_user == "uk" or local_user == "ia":
                msg = await ctx.followup.send(embed=disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-TITLE")["uk"],
                                                                  description=f'{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART1")["uk"]} {info["title"]}\n'
                                                                              f'{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART2")["uk"]} '
                                                                              f'{author_name_list[0]}',
                                                                  colour=disnake.Colour.brand_green()),
                                              view=ControlPanel())

            else:
                msg = await ctx.followup.send(embed=disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-TITLE")["en-US"],
                                                                  description=f'{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART1")["en-US"]} {info["title"]}\n'
                                                                              f'{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART2")["en-US"]} '
                                                                              f'{author_name_list[0]}',
                                                                  colour=disnake.Colour.brand_green()),
                                              view=ControlPanel())

            while vc.is_playing() or vc.is_paused():
                await asyncio.sleep(1)

            await msg.delete()

            if not len(list_of_songs) < 1:
                list_of_songs.pop(0)
                author_play_list.pop(0)
                author_name_list.pop(0)

        vc = ctx.guild.voice_client

        # Проверка для автоматичнского выхода
        if not vc.is_paused():
            await sleep(60)
            if not vc.is_playing() and vc:
                await vc.disconnect()


    @commands.slash_command(description=disnake.Localized(key="LEAVE-COMMAND-DESCRIPTIONS"))
    async def leave(self, ctx):
        voice = ctx.guild.voice_client

        user_local = str(ctx.locale)

        if ctx.user.voice is None:

            if user_local == "ru":
                emb_error = disnake.Embed(title=self.bot.i18n.get(key="LEAVE-ERROR_EMBED-TITLE")["ru"],
                                          description=self.bot.i18n.get(key="LEAVE-ERROR_EMBED-DESCRIPTIONS")["ru"],
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

            elif user_local == "uk" or user_local == "ua":
                emb_error = disnake.Embed(title=self.bot.i18n.get(key="LEAVE-ERROR_EMBED-TITLE")["uk"],
                                          description=self.bot.i18n.get(key="LEAVE-ERROR_EMBED-DESCRIPTIONS")["uk"],
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)

            else:
                emb_error = disnake.Embed(title=self.bot.i18n.get(key="LEAVE-ERROR_EMBED-TITLE")["en-US"],
                                          description=self.bot.i18n.get(key="LEAVE-ERROR_EMBED-DESCRIPTIONS")["en-US"],
                                          colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb_error, ephemeral=True)
            return
        if voice and voice.is_connected():
            if voice.is_playing:
                voice.stop()
            await voice.disconnect()

            if user_local == "ru":
                emb = disnake.Embed(description=self.bot.i18n.get(key="LEAVE-SUCCESS_EMBED-TITLE")["ru"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb)

            elif user_local == "uk" or user_local == "ua":
                emb = disnake.Embed(description=self.bot.i18n.get(key="LEAVE-SUCCESS_EMBED-TITLE")["ua"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb)

            else:
                emb = disnake.Embed(description=self.bot.i18n.get(key="LEAVE-SUCCESS_EMBED-TITLE")["en-US"],
                                    colour=disnake.Colour.green())

                await ctx.response.send_message(embed=emb)

        else:
            if user_local == "ru":
                emb = disnake.Embed(title=self.bot.i18n.get(key="LEAVE-ERROR_EMBED2")["ru"],
                                    colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb, delete_after=10)

            elif user_local == "uk" or user_local == "ua":
                emb = disnake.Embed(title=self.bot.i18n.get(key="LEAVE-ERROR_EMBED2")["uk"],
                                    colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb, delete_after=10)

            else:
                emb = disnake.Embed(title=self.bot.i18n.get(key="LEAVE-ERROR_EMBED2")["en-US"],
                                    colour=disnake.Colour.red())

                await ctx.response.send_message(embed=emb, delete_after=10)


def setup(bot):
    bot.add_cog(MusicCommands(bot))
