import asyncio
import disnake
import dotenv
import os
import spotipy
import yt_dlp as youtube_dl
from yt_dlp.utils._utils import DownloadError, ExtractorError
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from disnake.ext import commands
from disnake.errors import ClientException
from disnake import Localized
from asyncio import sleep
from datetime import timedelta
from typing import Optional
from bot import i18n_emb_message

linked_allowed = ["https://www.youtube.com/", "https://youtu.be/", "http://youtu.be/", "https://youtube.com/", "https://music.youtube.com",
                  "https://m.youtube.com/", "http://m.youtube.com/", "https://www.twitch.tv/", "https://soundcloud.com/",
                  "https://on.soundcloud.com/", "https://drive.google.com/", "https://open.spotify.com/"]

class ControlPanel(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = Optional[bool]
        self.list_songs = MusicCommands.list_of_songs
        self._user_id = MusicCommands.author_id_list

    async def user_check(self, ctx):
        if ctx.user.voice is None:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-VOICE-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-VOICE-DESCRIPTION",
                                   colour=disnake.Color.red(), delete_after=10, ephemeral=True, response=True)
            return False

        if ctx.author.id != 843213314163081237:
            if str(ctx.author.id) != self._user_id[0]:
                await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-USER-TITLE",
                                       "PLAY-COMMAND-ERROR_BUTTON-USER-DESCRIPTION",
                                       desc_extra=self.list_songs[self._user_id[0]]["name"],
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
        user_songs = self.list_songs[self._user_id[0]]

        if await self.user_check(ctx) is False:
            return

        if isinstance(user_songs["urls"][0], list):
            user_songs["urls"][0].insert(0, user_songs["urls"][0][0])
        else:
            user_songs["urls"].insert(0, user_songs["urls"][0])
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

        author_id = self._user_id[0]

        if vc.is_playing() or vc.is_paused():
            vc.stop()

        for i in range(self._user_id.count(author_id)):
            self._user_id[self._user_id.index(author_id)] = None

        self.list_songs[author_id]["urls"].clear()

        await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_STOP", colour=disnake.Colour.red(), delete_after=5,
                               response=True)

        self.value = True


class MusicCommands(commands.Cog):
    list_of_songs: dict = {}
    author_id_list: list = []

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        dotenv.load_dotenv(dotenv.find_dotenv())
        auth_manager = SpotifyClientCredentials(client_id=os.environ["CLIENT_ID"],
                                                client_secret=os.environ["CLIENT_SECRET"])
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)
        self.ctx = None
        self.playlist = 0
        self._YDL_OPTIONS = {
            'format': '234/140/233',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'preferfreeformats': True,
            'noplaylist': True,
            'quiet': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'no_warnings': True,
            'keepvideo': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'best',
                'preferredquality': '192',
            }],
        }
        self._FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                                "options": "-vn"}

    @staticmethod
    def check_link(url):
        for i in linked_allowed:
            if url.startswith(i):
                return True
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

    async def play_audio(self, ctx, url):
        source = disnake.FFmpegPCMAudio(url, executable="ffmpeg", **self._FFMPEG_OPTIONS)

        vc = ctx.guild.voice_client

        if not vc and ctx.user.voice:
            await ctx.user.voice.channel.connect()
            vc = ctx.guild.voice_client

        try:
            vc.play(source)
        except ClientException:
            await vc.connect(reconnect=True, timeout=60)
            vc = ctx.guild.voice_client
            vc.play(source)
        return vc

    async def restart_play_command(self, ctx):
        await self.play(ctx, url=self.list_of_songs[self.author_id_list[0]]["urls"].pop(0), playlist_count=0)

    def spotify_track(self, url, playlist_count, author_id) -> bool:
        if url.startswith("https://open.spotify.com/album"):
            self.extract_tracks(self.spotify.album_tracks(url)["items"], playlist_count, author_id)
            return True
        elif url.startswith("https://open.spotify.com/playlist"):
            self.extract_tracks(self.spotify.playlist_items(url)["items"], playlist_count, author_id)
            return True
        elif url.startswith("https://open.spotify.com/"):
            self.list_of_songs[author_id]["urls"].append(self.extract_video_info(self.spotify.track(url)))
            self.author_id_list.append(author_id)
            return True
        return False

    def extract_tracks(self, tracks, playlist_count, author_id):
        if tracks[0].get("added_at"):
            for i in range(len(tracks)):
                tracks[i] = tracks[i]["track"]
        if playlist_count == 0 or playlist_count == 1:
            self.list_of_songs[author_id]["urls"].append(self.extract_video_info(tracks[0]))
            self.author_id_list.append(author_id)
        elif len(tracks) < playlist_count:
            for i in range(len(tracks)):
                track_info = self.extract_video_info(tracks[i])
                self.list_of_songs[author_id]["urls"].append((track_info, (i+1, len(tracks))))
                self.author_id_list.append(author_id)
        else:
            for i in range(playlist_count):
                track_info = self.extract_video_info(tracks.pop(0))
                self.list_of_songs[author_id]["urls"].append((track_info, (i+1, playlist_count)))
                self.author_id_list.append(author_id)

    def extract_video_info(self, track_info) -> str:
        performers = ""
        music = track_info["name"]
        for names in track_info["artists"]:
            performers = performers + names["name"] + ", "
        performers = performers.rstrip(", ")
        return self.search_video(music, performers)

    def search_video(self, music, performers) -> str:
        videos_search = VideosSearch(f"{performers} - {music}", limit=1)
        videos_search = videos_search.result()["result"][0]["link"]
        return videos_search

    async def download_video(self, options, song) -> dict:
        with youtube_dl.YoutubeDL(options) as ydl:
            return ydl.extract_info(song, download=False)

    async def check_current_voice(self, member):
        vc = member.guild.voice_client
        await asyncio.sleep(120)

        if member.voice and member.voice.channel.id == disnake.utils.get(self.bot.voice_clients, guild=member.guild):
            return

        vc.stop()

        author_id = self.author_id_list[0]
        self.list_of_songs[author_id]["urls"].clear()
        count = self.author_id_list.count(author_id)
        for i in range(count):
            self.author_id_list[self.author_id_list.index(author_id)] = None

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if len(self.author_id_list) == 0:
            return
        if int(self.author_id_list[0]) == member.id:
            if after.channel is None:
                await self.check_current_voice(member)
            elif after.channel and after.channel.id != member.voice.channel.id:
                await self.check_current_voice(member)
            return



    @commands.slash_command(description=Localized(key="PLAY-COMMAND-DESCRIPTIONS"))
    async def play(self, ctx,
                   url: str = commands.param(description=Localized(key="PLAY-COMMAND-DESCRIPTIONS_PARAMETERS")),
                   playlist_count: int = commands.param(default=0)):
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

        if url in linked_allowed[:6]:
            self._YDL_OPTIONS["format"] = "234/140/233"
        else:
            self._YDL_OPTIONS["format"] = "bestaudio.2/bestaudio"

        if not self.list_of_songs.get(author_id):
            self.list_of_songs.update({author_id: {"name": ctx.author.global_name, "avatar": ctx.author.display_avatar, "lang": local_user, "urls": []}})

        if not self.spotify_track(url, playlist_count, author_id):
            if playlist_count > 1:
                ydl_opts = self._YDL_OPTIONS.copy()
                ydl_opts["noplaylist"] = False
                ydl_opts["playlistend"] = "1"

                start = []
                for i in url[::-1]:
                    try:
                        int(i)
                    except ValueError:
                        break
                    start.insert(0, i)

                for c in range(playlist_count):
                    self.author_id_list.append(author_id)

                if len(start) > 0:
                    start = "".join(start)
                    ydl_opts["playlistitems"] = f"{start}:{int(start) + playlist_count}"
                    ydl_opts["playlistend"] = playlist_count
                self.list_of_songs[author_id]["urls"].append((url, ydl_opts))
            else:
                self.list_of_songs[author_id]["urls"].append(url)
                self.author_id_list.append(author_id)


        await i18n_emb_message(ctx, False, "PLAY-COMMAND-ADD_LIST", colour=disnake.Colour.green(), delete_after=2)

        vc = ctx.guild.voice_client

        if vc and vc.is_playing():
            return

        while len(self.author_id_list) > 0:
            i = self.author_id_list[0]
            if i is None:
                self.author_id_list.pop(0)
                continue

            songs_list = self.list_of_songs[i]

            while len(songs_list["urls"]) > 0 and self.author_id_list[0] == i:
                emb = disnake.Embed(title=None, description=self.bot.i18n.get("PLAY-COMMAND-BUTTON_SKIP")[songs_list["lang"]],
                                    colour=disnake.Colour.green())
                msg = await ctx.channel.send(embed=emb)
                playlist_info = None

                if isinstance(songs_list["urls"][0], tuple) and isinstance(songs_list["urls"][0][-1], tuple):
                    info = await self.download_video(self._YDL_OPTIONS, songs_list["urls"][0][0])
                    playlist_info = (songs_list["urls"][0][-1][-1], songs_list["urls"][0][-1][0])
                elif isinstance(songs_list["urls"][0], tuple):
                    info = await self.download_video(songs_list["urls"][0][-1], songs_list["urls"][0][0])
                elif isinstance(songs_list["urls"][0], list):
                    info = songs_list["urls"][0][0]
                    playlist_info = (info.get("__last_playlist_index"), info.get("playlist_index"))
                else:
                    info = await self.download_video(self._YDL_OPTIONS, songs_list["urls"][0])

                await msg.delete()

                entries = info.get("entries")
                if entries and len(entries) > 1:
                    songs_list["urls"][0] = entries
                    info = songs_list["urls"][0][0]
                    playlist_info = (str(len(songs_list["urls"][0])), info["playlist_index"])

                URL = info["url"]

                if URL.startswith("https://manifest.googlevideo.com/"):
                    msg_info = await i18n_emb_message(ctx, "PLAY-COMMAND-FFMPEG-ERROR_EMBED-TITLE",
                                                      "PLAY-COMMAND-FFMPEG-ERROR_EMBED-DESCRIPTION", ephemeral=True)
                    if self._YDL_OPTIONS["format"] != "234/233/140":
                        self._YDL_OPTIONS["format"] = "best"
                    info = await self.download_video(self._YDL_OPTIONS, info["webpage_url"])
                    URL = info["url"]
                    await msg_info.delete()

                vc = await self.play_audio(ctx, URL)

                emb = disnake.Embed(title=None,
                                    description=f"{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART1")[songs_list["lang"]]} "
                                                f"{info.get("creator")}\n"
                                                f"{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-DESCRIPTION_PART2")[songs_list["lang"]]} "
                                                f"{timedelta(seconds=info["duration"] if info.get("duration") else 0)}",
                                    colour=disnake.Colour.brand_green())

                if playlist_info is not None:
                    emb.add_field(name=f"{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-PLAYLIST-VIDEO_INDEX")[songs_list["lang"]]} "
                                       f"{playlist_info[-1]}",
                                  value=f"{self.bot.i18n.get(key="PLAY-COMMAND-INFO_EMBED-PLAYLIST-COUNT")[songs_list["lang"]]} "
                                        f"{playlist_info[0]}")

                emb.set_author(name=f"{info["title"]}", url=info["webpage_url"],
                               icon_url=info["thumbnails"][-1]["url"])

                emb.set_footer(text=songs_list["name"], icon_url=songs_list["avatar"])

                msg = await ctx.channel.send(embed=emb, view=ControlPanel())

                while vc.is_playing() or vc.is_paused():
                    await sleep(1)

                vc.stop()

                await msg.delete()
                if not len(songs_list["urls"]) < 1:
                    if isinstance(songs_list["urls"][0], list) and len(songs_list["urls"][0]) > 1:
                        songs_list["urls"][0].pop(0)
                    else:
                        songs_list["urls"].pop(0)
                    self.author_id_list.pop(0)

            self.list_of_songs.clear()
            self.author_id_list.clear()

            if not vc.is_paused():
                await sleep(60)
                if not vc.is_playing() and vc:
                    await vc.disconnect()

    @play.error
    async def play_error(self, ctx, error):
        author_id = self.author_id_list.pop(0)
        songs_list = self.list_of_songs[author_id]

        if isinstance(error, ExtractorError):
            emb_err = disnake.Embed(title="ExtractError",
                                    description=f"{self.bot.i18n.get(key="PLAY-COMMAND-ERROR_EMBED-DESCRIPTION1")[songs_list["lang"]]}\n"
                                                f"{self.bot.i18n.get(key="PLAY-COMMAND-ERROR_EMBED-DESCRIPTION2")[songs_list["lang"]]}\n"
                                                f"```{error}```", colour=disnake.Colour.red())
        elif isinstance(error, DownloadError):
            emb_err = disnake.Embed(title="DownloadError",
                                    description=f"{self.bot.i18n.get(key="PLAY-COMMAND-ERROR_EMBED-DESCRIPTION1")[songs_list["lang"]]}\n"
                                                f"{self.bot.i18n.get(key="PLAY-COMMAND-ERROR_EMBED-DESCRIPTION2")[songs_list["lang"]]}\n"
                                                f"```{error}```", colour=disnake.Colour.red())
        else:
            emb_err = disnake.Embed(title="Error",
                                    description=f"{self.bot.i18n.get(key="PLAY-COMMAND-ERROR_EMBED-DESCRIPTION2")[songs_list["lang"]]}\n"
                                                f"```{error}```", colour=disnake.Colour.red())
        emb_err.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar)
        await ctx.send(embed=emb_err, ephemeral=True)

        if isinstance(songs_list["urls"][0], list) and len(songs_list["urls"][0]) > 1:
            songs_list["urls"][0].pop(0)
        else:
            songs_list["urls"].pop(0)

        if len(self.list_of_songs.keys()) > 0 and len(self.author_id_list) > 0:
            await self.restart_play_command(ctx)
        else:
            self.list_of_songs.clear()
            self.author_id_list.clear()

        print(error)


def setup(bot):
    bot.add_cog(MusicCommands(bot))
