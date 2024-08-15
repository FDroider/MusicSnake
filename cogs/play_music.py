import asyncio
import disnake
import yt_dlp as youtube_dl
from disnake.ext import commands
from disnake import Localized
from asyncio import sleep
from datetime import timedelta
from typing import Optional
from bot import i18n_emb_message

linked_allowed = ("https://www.youtube.com/", "https://youtu.be/", "http://youtu.be/", "https://youtube.com/",
                  "https://m.youtube.com/", "http://m.youtube.com/", "https://www.twitch.tv/")


class ControlPanel(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = Optional[bool]
        self.list_songs = MusicCommands.list_of_songs
        self._user_id = MusicCommands._author_id_list

    async def user_check(self, ctx):
        if ctx.user.voice is None:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-VOICE-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-VOICE-DESCRIPTION",
                                   colour=disnake.Color.red(), delete_after=10, ephemeral=True, response=True)
            return False

        if ctx.author.id != 843213314163081237:
            if str(ctx.author.id) != MusicCommands._author_id_list[0]:
                await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-USER-TITLE",
                                       "PLAY-COMMAND-ERROR_BUTTON-USER-DESCRIPTION",
                                       desc_extra=self.list_songs[MusicCommands._author_id_list[0]][0],
                                       colour=disnake.Colour.red(), delete_after=10, ephemeral=True, response=True)
                return False
        return True

    @disnake.ui.button(label="Pause", style=disnake.ButtonStyle.primary, row=1)
    async def pause(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if await self.user_check(ctx) is False:
            return

        if vc.is_playing():
            vc.pause()
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_PAUSE", colour=disnake.Colour.green(),
                                   delete_after=5, ephemeral=True, response=True)
        else:
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_PAUSE-ERROR",
                                   colour=disnake.Colour.brand_red(), delete_after=5, ephemeral=True, response=True)
        self.value = True

    @disnake.ui.button(label="Resume", style=disnake.ButtonStyle.green, row=1)
    async def resume(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if await self.user_check(ctx) is False:
            return

        if vc.is_paused():
            vc.resume()

            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_RESUME", colour=disnake.Colour.green(),
                                   delete_after=5, ephemeral=True, response=True)
        else:
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_RESUME-ERROR",
                                   colour=disnake.Colour.brand_red(), delete_after=5, ephemeral=True, response=True)

        self.value = True

    @disnake.ui.button(label="Replay", style=disnake.ButtonStyle.success, row=1)
    async def replay(self, button: disnake.ui.Button, ctx):
        _author_id = self._user_id[0]

        if await self.user_check(ctx) is False:
            return

        self.list_songs[_author_id][2].insert(0, self.list_songs[_author_id][2][0])
        self._user_id.insert(0, self._user_id[0])
        await i18n_emb_message(ctx, False, "PLAY-COMMAND-ADD_LIST", colour=disnake.Colour.green(), delete_after=2,
                               response=True)

    @disnake.ui.button(label="Skip", style=disnake.ButtonStyle.red, row=2)
    async def skip(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if await self.user_check(ctx) is False:
            return

        if not len(self._user_id) > 1:
            await i18n_emb_message(ctx, "PLAY-COMMAND-BUTTON_SKIP-ERROR-TITLE",
                                   "PLAY-COMMAND-BUTTON_SKIP-ERROR-DESCRIPTION", colour=disnake.Colour.red(),
                                   delete_after=10, ephemeral=True, response=True)

        elif vc.is_playing() or vc.is_paused():
            vc.stop()

        self.value = True

    @disnake.ui.button(label="Stop", style=disnake.ButtonStyle.red, row=2)
    async def stop(self, button: disnake.ui.Button, ctx):
        vc = ctx.guild.voice_client

        if await self.user_check(ctx) is False:
            return

        _author_id = self._user_id[0]

        if vc.is_playing():
            vc.stop()

        elif vc.is_paused():
            vc.stop()

        count = self._user_id.count(_author_id)
        for i in range(count):
            self._user_id[self._user_id.index(_author_id)] = None
        for i in MusicCommands._playlist_info:
            if i[0] == _author_id:
                MusicCommands._playlist_info.remove(i)
        self.list_songs[_author_id][2].clear()

        await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_STOP", colour=disnake.Colour.red(), delete_after=5,
                               response=True)

        self.value = True


class MusicCommands(commands.Cog):
    list_of_songs: dict = {}
    _author_id_list: list = []
    _playlist_info = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'preferfreeformats': True,
            'noplaylist': True,
            'quiet': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'best',
                'preferredquality': '5',
            }],
        }
        self._FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
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

    def get_index(self, item, info, key=None):
        if isinstance(info, list) and isinstance(info[0], tuple):
            for u in info:
                if u[0] == item:
                    return info.index(u)
        elif isinstance(info, list) and isinstance(info[0], dict):
            for i in info:
                if key:
                    if i[key] == item:
                        return info.index(i)
                else:
                    if item == i:
                        return info.index(i)
        return None

    @commands.slash_command(description=Localized(key="PLAY-COMMAND-DESCRIPTIONS"))
    async def play(self, ctx,
                   url: str = commands.param(description=Localized(key="PLAY-COMMAND-DESCRIPTIONS_PARAMETERS")),
                   playlist: bool = commands.param(default=False)):
        await ctx.response.defer()

        local_user = str(ctx.locale)
        author_id = str(ctx.author.id)

        if local_user not in ("ru", "uk", "en-US"):
            local_user = "en-US"

        try:
            if ctx.user.voice is None:
                await i18n_emb_message(ctx, "PLAY-COMMAND-VOICE-ERROR_EMBED-TITLE",
                                       "PLAY-COMMAND-VOICE-ERROR_EMBED-DESCRIPTION", colour=disnake.Colour.red())
                return
        except AttributeError:
            await ctx.followup.send(embed=disnake.Embed(title="Error", description="Support only for guilds",
                                                        colour=disnake.Colour.red()))
            return

        if self.check_link(url) is False:
            await i18n_emb_message(ctx, "PLAY-COMMAND-SUPPORT-ERROR_EMBED-TITLE",
                                   "PLAY-COMMAND-SUPPORT-ERROR_EMBED-DESCRIPTION", colour=disnake.Colour.red())
            return

        self._YDL_OPTIONS["noplaylist"] = not playlist
        if playlist:
            start = []
            for i in url[::-1]:
                try:
                    int(i)
                except ValueError:
                    break
                start.insert(0, i)
            if len(start) > 0:
                start = "".join(start)
                self._YDL_OPTIONS["playlistitems"] = f"{start}:{int(start)+15}"
                self._YDL_OPTIONS["playlistend"] = "15"

        if not self.list_of_songs.get(author_id):
            self.list_of_songs.update({author_id: (ctx.author.global_name, ctx.author.display_avatar, [])})
        self.list_of_songs[author_id][2].append(url)
        self._author_id_list.append(author_id)

        await i18n_emb_message(ctx, False, "PLAY-COMMAND-ADD_LIST", colour=disnake.Colour.green(), delete_after=2)

        vc = ctx.guild.voice_client

        if vc and vc.is_playing():
            return

        while len(self._author_id_list) > 0:
            i = self._author_id_list[0]
            if i is None:
                self._author_id_list.pop(0)
                continue
            while len(self.list_of_songs[i][2]) > 0:
                emb = disnake.Embed(title=None, description=self.bot.i18n.get("PLAY-COMMAND-BUTTON_SKIP")[local_user],
                                    colour=disnake.Colour.green())
                msg = await ctx.channel.send(embed=emb)

                if len(self._playlist_info) >= 1 and self._playlist_info[0][0] == i:
                    info = self._playlist_info[self.get_index(i, self._playlist_info)][1]
                    info = info[self.get_index(self.list_of_songs.get(i)[2][0], info, "original_url")]
                else:
                    with youtube_dl.YoutubeDL(self._YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(self.list_of_songs.get(i)[2][0], download=False)

                await msg.delete()

                URL = None
                if info.get("entries") and len(info.get("entries")) > 1:
                    self._playlist_info.append((i, []))
                    self._author_id_list.pop()
                    for v in info["entries"]:
                        if self.list_of_songs[i][2][-1].startswith(v["original_url"]):
                            self.list_of_songs[i][2].pop()
                            URL = v["url"]
                        self._playlist_info[-1][1].append(v)
                        self._author_id_list.append(i)
                        self.list_of_songs[i][2].append(v["original_url"])
                    info = info["entries"][0]
                else:
                    URL = info["url"]

                source = disnake.FFmpegPCMAudio(URL, executable="ffmpeg", **self._FFMPEG_OPTIONS)
                vc = ctx.guild.voice_client

                if vc is None or not vc:
                    await ctx.user.voice.channel.connect()
                    vc = ctx.guild.voice_client

                vc.play(source)

                emb = disnake.Embed(title=None,
                                    description=f"{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART1")[local_user]} "
                                                f"{info["creator"] if info.get("creator") else None}\n"
                                                f"{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART2")[local_user]} "
                                                f"{timedelta(seconds=info["duration"] if info.get("duration") else 0)}"
                                                f"{f'\n{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART3")[local_user]} {info["__last_playlist_index"]}' 
                                                    if len(self._playlist_info) >= 1 and self._playlist_info[0][0] == i else ""}",
                                    colour=disnake.Colour.brand_green())
                emb.set_author(name=f"{info["title"]} {f" - Playlist - {info["playlist_index"]}" if len(self._playlist_info) >= 1 and self._playlist_info[0][0] == i else ""}",
                               url=info["original_url"], icon_url=info["thumbnails"][-1]["url"])
                emb.set_footer(text=self.list_of_songs[i][0], icon_url=self.list_of_songs[i][1])

                msg = await ctx.channel.send(embed=emb, view=ControlPanel())

                while vc.is_playing() or vc.is_paused():
                    await asyncio.sleep(1)
                    if ctx.user.voice is None:
                        await asyncio.sleep(10)
                        if ctx.user.voice is not None:
                            continue
                        vc.stop()

                await msg.delete()

                if not len(self.list_of_songs[i][2]) < 1:
                    self.list_of_songs[i][2].pop(0)
                    self._author_id_list.pop(0)
                    if not len(self._playlist_info) < 1:
                        if self._playlist_info[0][0] == i and not len(self._playlist_info[self.get_index(i, self._playlist_info)][1]) < 1:
                            self._playlist_info[self.get_index(i, self._playlist_info)][1].pop(0)
                        else:
                            self._playlist_info.pop(0)

        self.list_of_songs.clear()

        if not vc.is_paused():
            await sleep(60)
            if not vc.is_playing() and vc:
                await vc.disconnect()


def setup(bot):
    bot.add_cog(MusicCommands(bot))
