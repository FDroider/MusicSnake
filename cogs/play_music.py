import asyncio
import disnake
import yt_dlp as youtube_dl
from disnake.ext import commands
from disnake import Localized
from asyncio import sleep
from typing import Optional
from bot import i18n_emb_message, i18n_message

linked_allowed = ("https://www.youtube.com/", "https://youtu.be/", "http://youtu.be/", "https://youtube.com/",
                  "https://m.youtube.com/", "http://m.youtube.com/", "https://www.twitch.tv/")

list_of_songs = []
author_play_list = []
author_name_list = []


class ControlPanel(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = Optional[bool]

    @disnake.ui.button(label="Pause", style=disnake.ButtonStyle.primary, row=1)
    async def pause(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if ctx.user.voice is None:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-VOICE-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-VOICE-DESCRIPTION",
                                   colour=disnake.Color.red(), delete_after=10, ephemeral=True, response=True)
            return

        if ctx.author.id != 843213314163081237:
            if author_play_list[0] != ctx.author.id:
                await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-USER-TITLE",
                                       "PLAY-COMMAND-ERROR_BUTTON-USER-DESCRIPTION", desc_extra=author_name_list[0],
                                       colour=disnake.Colour.red(), delete_after=10, ephemeral=True, response=True)
                return

        if vc.is_playing():
            vc.pause()
            await i18n_message(ctx, "PLAY-COMMAND-BUTTON_PAUSE", delete_after=5, ephemeral=True)
        else:
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_PAUSE-ERROR",
                                   colour=disnake.Colour.brand_red(), delete_after=5, ephemeral=True, response=True)
        self.value = True

    @disnake.ui.button(label="Resume", style=disnake.ButtonStyle.green, row=1)
    async def resume(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if ctx.user.voice is None:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-VOICE-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-VOICE-DESCRIPTION",
                                   colour=disnake.Color.red(), delete_after=10, ephemeral=True, response=True)
            return

        if ctx.author.id != 843213314163081237:
            if author_play_list[0] != ctx.author.id:
                await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-USER-TITLE",
                                       "PLAY-COMMAND-ERROR_BUTTON-USER-DESCRIPTION", desc_extra=author_name_list[0],
                                       colour=disnake.Colour.red(), delete_after=10, ephemeral=True, response=True)
                return

        if vc.is_paused():
            vc.resume()

            await i18n_message(ctx, "PLAY-COMMAND-BUTTON_RESUME", delete_after=5, ephemeral=True)
        else:
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_RESUME-ERROR",
                                   colour=disnake.Colour.brand_red(), delete_after=5, ephemeral=True, response=True)

        self.value = True

    @disnake.ui.button(label="Replay", style=disnake.ButtonStyle.success, row=1)
    async def replay(self, button: disnake.ui.Button, ctx):

        if ctx.user.voice is None:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-VOICE-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-VOICE-DESCRIPTION",
                                   colour=disnake.Color.red(), delete_after=10, ephemeral=True, response=True)
            return

        if ctx.author.id != 843213314163081237:
            if author_play_list[0] != ctx.author.id:
                await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-USER-TITLE",
                                       "PLAY-COMMAND-ERROR_BUTTON-USER-DESCRIPTION", desc_extra=author_name_list[0],
                                       colour=disnake.Colour.red(), delete_after=10, ephemeral=True, response=True)
                return

        list_of_songs.append(list_of_songs[0])
        author_name_list.append(author_name_list[0])
        author_play_list.append(author_play_list[0])
        await i18n_message(ctx, "PLAY-COMMAND-ADD_LIST", delete_after=2)

    @disnake.ui.button(label="Skip", style=disnake.ButtonStyle.red, row=2)
    async def skip(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if ctx.user.voice is None:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-VOICE-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-VOICE-DESCRIPTION",
                                   colour=disnake.Color.red(), delete_after=10, ephemeral=True, response=True)
            return

        if ctx.author.id != 843213314163081237:
            if author_play_list[0] != ctx.author.id:
                await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-USER-TITLE",
                                       "PLAY-COMMAND-ERROR_BUTTON-USER-DESCRIPTION", desc_extra=author_name_list[0],
                                       colour=disnake.Colour.red(), delete_after=10, ephemeral=True, response=True)
                return

        if len(list_of_songs) <= 1:
            await i18n_emb_message(ctx, "PLAY-COMMAND-BUTTON_SKIP-ERROR-TITLE",
                                   "PLAY-COMMAND-BUTTON_SKIP-ERROR-DESCRIPTION", colour=disnake.Colour.red(),
                                   delete_after=10, ephemeral=True, response=True)

        elif vc.is_playing():
            vc.stop()
            await i18n_message(ctx, "PLAY-COMMAND-BUTTON_SKIP", delete_after=5)
        elif vc.is_paused():
            vc.stop()
            await i18n_message(ctx, "PLAY-COMMAND-BUTTON_SKIP", delete_after=5)

        self.value = True

    @disnake.ui.button(label="Stop", style=disnake.ButtonStyle.red, row=2)
    async def stop(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if ctx.user.voice is None:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-VOICE-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-VOICE-DESCRIPTION", colour=disnake.Colour.red(),
                                   delete_after=5, ephemeral=True, response=True)
            return

        if ctx.author.id != 843213314163081237:
            if author_play_list[0] != ctx.author.id:
                await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-USER-TITLE",
                                       "PLAY-COMMAND-ERROR_BUTTON-USER-DESCRIPTION",
                                       desc_extra=author_name_list[0],
                                       colour=disnake.Colour.red(), delete_after=5, ephemeral=True, response=True)
                return

        if vc.is_playing():
            list_of_songs.clear()
            author_play_list.clear()
            author_name_list.clear()
            vc.stop()

        elif vc.is_paused():
            list_of_songs.clear()
            author_play_list.clear()
            author_name_list.clear()
            vc.stop()

        await i18n_message(ctx, "PLAY-COMMAND-BUTTON_STOP", 5)

        self.value = True


class MusicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'preferfreeformats': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'best',
                'preferredquality': '5',
            }],
        }
        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                               "options": "-vn"}

    # Функция проверки ссылки
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
            await i18n_emb_message(ctx, "PLAY-COMMAND-VOICE-ERROR_EMBED-TITLE",
                                   "PLAY-COMMAND-VOICE-ERROR_EMBED-DESCRIPTION", colour=disnake.Colour.red())
            return

        # Проверяем на поддержку силку на виде
        if self.check_link(url) is False:
            await i18n_emb_message(ctx, "PLAY-COMMAND-SUPPORT-ERROR_EMBED-TITLE",
                                   "PLAY-COMMAND-SUPPORT-ERROR_EMBED-DESCRIPTION", colour=disnake.Colour.red())
            return

        # Подсойдинение к войс чату
        try:
            await ctx.user.voice.channel.connect()

            list_of_songs.append(url)
            author_play_list.append(ctx.author.id)
            author_name_list.append(ctx.author.display_name)
        except Exception as e:
            print(f"[Log]Already connect or don`t connect to voice\nError message: {e}")

            list_of_songs.append(url)
            author_play_list.append(ctx.author.id)
            author_name_list.append(ctx.author.display_name)

        await i18n_emb_message(ctx, False, "PLAY-COMMAND-ADD_LIST", colour=disnake.Colour.green(), delete_after=2)

        while len(list_of_songs) > 0:

            if len(list_of_songs) > 1:
                return

            with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(list_of_songs[0], download=False)  # Загрузка видео без скачки

            # URL = ydl.sanitize_info(info)
            URL = info['url']  # Получение информации о url

            source = disnake.FFmpegPCMAudio(URL, executable="ffmpeg", **self.FFMPEG_OPTIONS)
            vc = ctx.guild.voice_client
            vc.play(source)  # Прогиеривание музыки

            if local_user not in ("ru", "uk", "en-US"):
                local_user = "en-US"

            msg = await ctx.channel.send(
                embed=disnake.Embed(title=self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-TITLE")[local_user],
                                    description=f'{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART1")[local_user]} {info["title"]}\n'
                                                f'{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART2")[local_user]} '
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


def setup(bot):
    bot.add_cog(MusicCommands(bot))
