import asyncio
import disnake
from disnake.ext import commands
from asyncio import sleep
from typing import Optional
from functools import lru_cache
import yt_dlp as youtube_dl

linked_allowed = ["https://www.youtube.com/", "https://youtu.be/", "https://youtube.com/",
                  "https://m.youtube.com/", "http://m.youtube.com/", "http://youtu.be/"]

list_of_songs = []
author_play_list = []
author_name_list = []


class ControlPanel(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.vol_new = float(8)
        self.value = Optional[bool]

    @disnake.ui.button(label="Pause", style=disnake.ButtonStyle.primary, row=1)
    async def pause(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if ctx.user.voice is None:
            emb_error = disnake.Embed(title="Ошибка 303",
                                      description="Вы не подключены к войс чату",
                                      colour=disnake.Colour.red())

            await ctx.response.send_message(embed=emb_error, ephemeral=True)

            return

        if not ctx.author.id == 843213314163081237:
            if not author_play_list[0] == ctx.author.id:
                emb_e = disnake.Embed(title="Ошибка",
                                      description=f"Сейчас руководит парадом пользаватель {author_name_list[0]}",
                                      colour=disnake.Colour.red())

                await ctx.send(embed=emb_e, ephemeral=True)

                return

        if vc.is_playing():
            vc.pause()
            await ctx.send("Пауза", delete_after=5, ephemeral=True)
        else:
            emb = disnake.Embed(description="Музыка уже не воспроизводится или закончилась",
                                colour=disnake.Colour.brand_red())
            await ctx.response.send_message(embed=emb, delete_after=5, ephemeral=True)

        self.value = True

    @disnake.ui.button(label="Resume", style=disnake.ButtonStyle.green, row=1)
    async def resume(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if ctx.user.voice is None:
            emb_error = disnake.Embed(title="Ошибка 303",
                                      description="Вы не подключены к войс чату",
                                      colour=disnake.Colour.red())

            await ctx.response.send_message(embed=emb_error, ephemeral=True)

            return

        if not ctx.author.id == 843213314163081237:
            if not author_play_list[0] == ctx.author.id:
                emb_e = disnake.Embed(title="Ошибка",
                                      description=f"Сейчас руководит парадом пользаватель {author_name_list[0]}",
                                      colour=disnake.Colour.red())

                await ctx.send(embed=emb_e, ephemeral=True)

                return

        if vc.is_paused():
            vc.resume()

            await ctx.send("Продолжаю проыгривать", delete_after=5, ephemeral=True)
        else:
            emb = disnake.Embed(description="Музыка уже воспроизводтся",
                                colour=disnake.Colour.brand_red())

            await ctx.response.send_message(embed=emb, delete_after=5, ephemeral=True)

        self.value = True

    @disnake.ui.button(label="Stop", style=disnake.ButtonStyle.red, row=1)
    async def stop(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if ctx.user.voice is None:
            emb_error = disnake.Embed(title="Ошибка 303",
                                      description="Вы не подключены к войс чату",
                                      colour=disnake.Colour.red())

            await ctx.response.send_message(embed=emb_error, ephemeral=True)

            return

        if not ctx.author.id == 843213314163081237:
            if not author_play_list[0] == ctx.author.id:
                emb_e = disnake.Embed(title="Ошибка",
                                      description=f"Сейчас руководит парадом пользаватель {author_name_list[0]}",
                                      colour=disnake.Colour.red())

                await ctx.send(embed=emb_e, ephemeral=True)

                return

        if vc.is_playing():
            vc.stop()

            await ctx.send("Воспроизведение прекращено", delete_after=5)

        elif vc.is_paused():
            vc.stop()

            await ctx.send("Воспроизведение прекращено", delete_after=5)

        self.value = True


@lru_cache(maxsize=None)
class MusicCommands(commands.Cog):
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

    @commands.slash_command(description="Воспроизводит музику из ютуба или youtube music")
    async def play(self, ctx, url: str):
        """
        Parameters
        ----------
        url: Сылка на youtube или youtube music
        """
        await ctx.response.defer()

        # Проверка что пользаватель находится в войс чате
        if ctx.user.voice is None:
            return await ctx.response.send_message(embed=disnake.Embed(title="Ощибка подключения",
                                                                       description="Зайдите в один из войс чатов "
                                                                                   "и включите музыку "
                                                                                   "что бы воспользавтся етой командой",
                                                                       colour=disnake.Colour.red()))

        # Подсойдинение к войс чату
        try:
            await ctx.user.voice.channel.connect()

            list_of_songs.append(url)
            author_play_list.append(ctx.author.id)
            author_name_list.append(ctx.author.name)
        except:
            print("[Log] Уже подключен или не удалось подключиться")

            list_of_songs.append(url)
            author_play_list.append(ctx.author.id)
            author_name_list.append(ctx.author.name)

            await ctx.send("Добавлено в очередь", delete_after=2)

        try:
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

                msg = await ctx.followup.send(embed=disnake.Embed(title="Сейчас играет",
                                                                  description=f"Название музикы: {info['title']}\n"
                                                                              f"Пользаватель который ее воспроизводит: "
                                                                              f"{author_name_list[0]}",
                                                                  colour=disnake.Colour.brand_green()),
                                              view=ControlPanel())

                while vc.is_playing() or vc.is_paused():
                    await asyncio.sleep(1)

                await msg.delete()

                list_of_songs.pop(0)
                author_play_list.pop(0)
                author_name_list.pop(0)

            vc = ctx.guild.voice_client

            # Проверка для автоматичнского выхода
            if not vc.is_paused():
                await sleep(60)
                if not vc.is_playing() and vc:
                    await vc.disconnect()
        except:
            vc = ctx.guild.voice_client
            emb = disnake.Embed(title="Ошибка воспроизведения",
                                description="Сылка не поддерживается!",
                                colour=disnake.Colour.red())

            await ctx.followup.send(embed=emb)

            if not vc.is_paused():
                await sleep(60)
                if not vc.is_playing() and vc:
                    await vc.disconnect()
            return

    @commands.slash_command(description="Вийти из войса")
    async def leave(self, ctx):
        voice = ctx.guild.voice_client
        if ctx.user.voice is None:
            return await ctx.response.send_message(embed=disnake.Embed(title="Ошибка 303",
                                                                       description="Бота нет в войсе",
                                                                       colour=disnake.Colour.red()),
                                                   ephemeral=True)
        if voice and voice.is_connected():
            if voice.is_playing:
                voice.stop()
            await voice.disconnect()

            await ctx.response.send_message(embed=disnake.Embed(description="Бот вишел из войса",
                                                                colour=disnake.Colour.green()))
        else:
            emb = disnake.Embed(title="Бот уже отключен от войса",
                                colour=disnake.Colour.red())

            await ctx.response.send_message(embed=emb, delete_after=10)


def setup(bot):
    bot.add_cog(MusicCommands(bot))
