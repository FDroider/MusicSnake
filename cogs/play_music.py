import asyncio
import disnake
import dotenv
import os
import spotipy
from functools import partial
from yt_dlp import YoutubeDL
from yt_dlp.utils._utils import DownloadError, ExtractorError
from spotipy.oauth2 import SpotifyClientCredentials
from disnake.ext import commands
from disnake import Localized
from datetime import timedelta
from typing import Optional
from bot import i18n_emb_message, get_i18n_value

LINK_ALLOWED = ["https://www.youtube.com/", "https://youtu.be/", "http://youtu.be/", "https://youtube.com/",
                "https://music.youtube.com", "https://m.youtube.com/", "http://m.youtube.com/", "https://www.twitch.tv/",
                "https://soundcloud.com/", "https://on.soundcloud.com/", "https://drive.google.com/",
                "https://open.spotify.com/"]

class ControlPanel(disnake.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.value = Optional[bool]
        self.cog = cog

    def get_current_list_song(self, guild_id):
        return self.cog.queues.get(guild_id)

    def set_list_song(self, guild_id, song_list):
        self.cog.queues.update({guild_id: song_list})

    async def user_check(self, ctx):
        if ctx.user.voice is None:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-VOICE-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-VOICE-DESCRIPTION",
                                   colour=disnake.Color.red(), delete_after=10, ephemeral=True, response=True)
            return False

        song_list = self.get_current_list_song(ctx.guild.id)
        if ctx.author.id != song_list[0]["author_id"] and ctx.author.id != ctx.guild.owner_id:
            await i18n_emb_message(ctx, "PLAY-COMMAND-ERROR_BUTTON-USER-TITLE",
                                   "PLAY-COMMAND-ERROR_BUTTON-USER-DESCRIPTION",
                                   desc_extra=song_list[0]["author_name"],
                                   colour=disnake.Colour.red(), delete_after=10, ephemeral=True, response=True)
            return False
        return True

    @disnake.ui.button(label="Pause", style=disnake.ButtonStyle.primary, row=1)
    async def pause(self, button: disnake.ui.Button, ctx):
        if not await self.user_check(ctx):
            return

        vc = ctx.guild.voice_client

        if vc and vc.is_playing():
            vc.pause()
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_PAUSE", colour=disnake.Colour.green(),
                                   delete_after=5, ephemeral=True, response=True)
        else:
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_PAUSE-ERROR",
                                   colour=disnake.Colour.brand_red(), delete_after=5, ephemeral=True, response=True)
        self.value = True

    @disnake.ui.button(label="Resume", style=disnake.ButtonStyle.green, row=1)
    async def resume(self, button: disnake.ui.Button, ctx):
        if not await self.user_check(ctx):
            return

        vc = ctx.guild.voice_client

        if vc and vc.is_paused():
            vc.resume()
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_RESUME", colour=disnake.Colour.green(),
                                   delete_after=5, ephemeral=True, response=True)
        else:
            await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_RESUME-ERROR",
                                   colour=disnake.Colour.brand_red(), delete_after=5, ephemeral=True, response=True)

        self.value = True

    @disnake.ui.button(label="Replay", style=disnake.ButtonStyle.success, row=1)
    async def replay(self, button: disnake.ui.Button, ctx):
        if not await self.user_check(ctx):
            return

        song_list = self.get_current_list_song(ctx.guild.id)

        song_list.insert(1, song_list[0])
        await i18n_emb_message(ctx, False, "PLAY-COMMAND-ADD_LIST", colour=disnake.Colour.green(), delete_after=2,
                               response=True)
        self.value = True

    @disnake.ui.button(label="Skip", style=disnake.ButtonStyle.red, row=2)
    async def skip(self, button: disnake.ui.Button, ctx):
        if not await self.user_check(ctx):
            return

        vc = ctx.guild.voice_client

        if not len(self.get_current_list_song(ctx.guild.id)) > 1:
            await i18n_emb_message(ctx, "PLAY-COMMAND-BUTTON_SKIP-ERROR-TITLE",
                                   "PLAY-COMMAND-BUTTON_SKIP-ERROR-DESCRIPTION", colour=disnake.Colour.red(),
                                   delete_after=10, ephemeral=True, response=True)

        elif vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()

        self.value = True

    @disnake.ui.button(label="Stop", style=disnake.ButtonStyle.red, row=2)
    async def stop(self, button: disnake.ui.Button, ctx):
        if not await self.user_check(ctx):
            return

        vc = ctx.guild.voice_client
        guild_id = ctx.guild.id

        song_list = [song for song in self.get_current_list_song(guild_id) if song["author_id"] != ctx.author.id]
        self.set_list_song(guild_id, song_list)

        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()

        await i18n_emb_message(ctx, False, "PLAY-COMMAND-BUTTON_STOP", colour=disnake.Colour.green(), delete_after=5,
                               response=True)

        self.value = True


class MusicCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues = {}
        self.voice_contexts = {}
        dotenv.load_dotenv(dotenv.find_dotenv())
        if os.environ.get("CLIENT_ID") and os.environ.get("CLIENT_SECRET"):
            auth_manager = SpotifyClientCredentials(client_id=os.environ["CLIENT_ID"],
                                                    client_secret=os.environ["CLIENT_SECRET"])
            self.spotify = spotipy.Spotify(auth_manager=auth_manager)
        else:
            self.spotify = None
            print("Error: Spotify not connected! Not found CLIENT_ID or CLIENT_SECRET")
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
        for i in LINK_ALLOWED:
            if url.startswith(i):
                return True
        return False

    def get_song_list(self, guild_id = None):
        if guild_id:
            return self.queues.get(guild_id)
        return self.queues

    async def get_video_data(self, url, options: dict = None, loop = None):
        if not options or options is None:
            options = self._YDL_OPTIONS
        if not loop or loop is None:
            loop = self.bot.loop
        pl = partial(YoutubeDL(options).extract_info, url, download=False)
        return await loop.run_in_executor(None, pl)

    async def get_playlist_data(self, url, playlist_count):
        ydl_opts = self._YDL_OPTIONS.copy()
        ydl_opts["noplaylist"] = False

        nums = []
        for i in url[::-1]:
            try:
                int(i)
            except ValueError:
                break
            nums.insert(0, i)
        if len(nums) > 0:
            start = "".join(nums)
            ydl_opts["playlistitems"] = f"{start}:{int(start) + playlist_count}"
            ydl_opts["playlistend"] = playlist_count
        return await self.get_video_data(url, ydl_opts)

    def parse_spotify_url(self, url, playlist_count):
        if not self.spotify:
            return None
        if "track" in url:
            track = self.spotify.track(url)
            return [f"{track['artists'][0]['name']} - {track['name']}"]
        elif "playlist" in url:
            playlist = self.spotify.playlist_items(url)
            tracks = []
            for i in range(len(playlist['items'][:playlist_count])):
                if playlist['items'][i]['track']:
                    track = playlist['items'][i]['track']
                    tracks.append((f"{track['artists'][0]['name']} - {track['name']}", i+1))
            return tracks
        elif "album" in url:
            album = self.spotify.album_tracks(url)
            tracks = []
            for i in range(len(album['items'][:playlist_count])):
                if album['items'][i]:
                    track = album['items'][i]
                    tracks.append((f"{track['artists'][0]['name']} - {track['name']}", i+1))
            return tracks
        return None

    def add_to_queue(self, ctx, locale, data, playlist: list = None):
        icon = data.get("thumbnails")
        if playlist:
            song_info = {
                "url": data.get("url"),
                "webpage_url": data.get("webpage_url"),
                "title": data.get("title"),
                "creator": data.get("creator"),
                "duration": data.get("duration"),
                "playlist_index": playlist[0],
                "playlist_count": playlist[1],
                "icon_url": icon[0]["url"] if isinstance(icon, list) else icon,
                "author_id": ctx.author.id,
                "author_name": ctx.author.global_name,
                "author_lang": locale
            }
        else:
            song_info = {
                "url": data.get("url"),
                "webpage_url": data.get("webpage_url"),
                "title": data.get("title"),
                "creator": data.get("creator"),
                "duration": data.get("duration"),
                "icon_url": icon[0]["url"] if isinstance(icon, list) else icon,
                "author_id": ctx.author.id,
                "author_name": ctx.author.global_name,
                "author_lang": locale
            }
        self.queues[ctx.guild.id].append(song_info)

    def play_next(self, ctx: disnake.Interaction, error = None, future_result = None):
        guild_id = ctx.guild.id
        if future_result:
            asyncio.run_coroutine_threadsafe(future_result.delete(), self.bot.loop)
        if guild_id in self.queues and len(self.queues[guild_id]) > 0:
            self.queues[ctx.guild.id].pop(0)
            self.play_audio(ctx, error)
        else:
            msg = i18n_emb_message(ctx, "PLAY-COMMAND-QUEUE-ENDED", colour=disnake.Colour.yellow(), delete_after=120)
            asyncio.run_coroutine_threadsafe(msg, self.bot.loop)
            self.bot.loop.create_task(self.afk_timer(ctx.guild))

    def play_audio(self, ctx: disnake.Interaction, error = None):
        vc = ctx.guild.voice_client

        if not vc or not vc.is_connected():
            return

        next_song = None
        guild_id = ctx.guild.id
        if guild_id in self.queues and len(self.queues[guild_id]) > 0:
            next_song = self.queues[guild_id][0]
        elif next_song is None:
            return

        url = next_song["url"]
        source = disnake.FFmpegPCMAudio(url, **self._FFMPEG_OPTIONS)
        emb = disnake.Embed(title=None,
                            description=
                            f"{get_i18n_value('PLAY-COMMAND-INFO_EMBED-CREATOR', next_song['author_lang'])} "
                            f"{next_song["creator"]}\n"
                            f"{get_i18n_value('PLAY-COMMAND-INFO_EMBED-DURATION', next_song['author_lang'])} "
                            f"{timedelta(seconds=next_song['duration'])}",
                            colour=disnake.Colour.brand_green())
        emb.set_author(name=f'{next_song["title"]}', url=next_song["webpage_url"], icon_url=next_song['icon_url'])
        emb.set_footer(text=ctx.author.global_name, icon_url=ctx.author.display_avatar)

        if next_song.get("playlist_index"):
            emb.add_field(
                name=f"{get_i18n_value('PLAY-COMMAND-INFO_EMBED-PLAYLIST-VIDEO_INDEX', next_song['author_lang'])} "
                     f"{next_song['playlist_index']}",
                value=f"{get_i18n_value('PLAY-COMMAND-INFO_EMBED-PLAYLIST-COUNT', next_song['author_lang'])} "
                      f"{next_song['playlist_count']}")

        async def send_message():
            view = ControlPanel(self)
            msg = await ctx.channel.send(embed=emb, view=view)
            return msg

        fut = asyncio.run_coroutine_threadsafe(send_message(), self.bot.loop)
        def callback(future):
            try:
                msg = future.result()
                vc.play(source, after=lambda e: self.play_next(ctx, e, msg))
            except Exception as e:
                print(f"SendError or PlayError!\nError: {e}")
        fut.add_done_callback(callback)

    async def afk_timer(self, guild):
        await asyncio.sleep(180)
        vc = guild.voice_client
        if not vc or not vc.is_connected():
            return
        if vc.is_playing() or vc.is_paused():
            return
        if not vc or not vc.is_connected():
            return
        await vc.disconnect()

    async def check_voice(self, member):
        await asyncio.sleep(120)
        vc = member.guild.voice_client
        guild_id = member.guild.id
        if not vc and vc.is_connected():
            return
        if member.voice and member.voice.channel and member.voice.channel.id == vc.channel.id:
            return
        queue = self.get_song_list(guild_id)
        if not queue:
            return

        if queue[0]["author_id"] == member.id:
            self.queues[guild_id] = [song for song in queue if song["author_id"] != member.id]

            if vc.is_playing() or vc.is_paused():
                vc.stop()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id:
            return
        queue = self.get_song_list(member.guild.id)
        if not queue or len(queue) == 0:
            return
        if queue[0]["author_id"] == member.id:
            if after.channel is None:
                await self.check_voice(member)
            elif after.channel and after.channel.id != member.voice.channel.id:
                await self.check_voice(member)

    @commands.slash_command(description=Localized(key="PLAY-COMMAND-DESCRIPTIONS"))
    async def play(self, ctx,
                   url: str = commands.Param(description=Localized(key="PLAY-COMMAND-DESCRIPTIONS_PARAMETERS")),
                   playlist_count: int = commands.Param(default=1)):
        vc = ctx.guild.voice_client
        await ctx.response.defer()

        if not ctx.user.voice:
            await i18n_emb_message(ctx, "PLAY-COMMAND-VOICE-ERROR_EMBED-TITLE",
                                   "PLAY-COMMAND-VOICE-ERROR_EMBED-DESCRIPTION", colour=disnake.Colour.red())
            return
        elif not vc:
            vc = await ctx.author.voice.channel.connect()
        elif vc.channel != ctx.author.voice.channel:
            await i18n_emb_message(ctx, "PLAY-COMMAND-VOICE-BUSY-ERROR_EMBED", title_extra="ErrorConnect",
                                   colour=disnake.Colour.red(), ephemeral=True)
            return

        if not self.check_link(url):
            await i18n_emb_message(ctx, "PLAY-COMMAND-VOICE-ERROR_EMBED-TITLE",
                                   "PLAY-COMMAND-VOICE-ERROR_EMBED-DESCRIPTION", colour=disnake.Colour.red())
            return

        locale = str(ctx.locale)
        if locale not in ("ru", "uk", "en-US"):
            locale = "en-US"

        guild_id = ctx.guild.id

        if guild_id not in self.queues:
            self.queues[guild_id] = []

        if "spotify.com" in url:
            msg_s = await i18n_emb_message(ctx, "PLAY-COMMAND-SPOTIFY-SEARCH", colour=disnake.Colour.yellow())
            spotify_tracks = self.parse_spotify_url(url, playlist_count)
            await msg_s.delete()
            if not spotify_tracks:
                await i18n_emb_message(ctx, "PLAY-COMMAND-SPOTIFY-NOT-FOUND", colour=disnake.Colour.red(),
                                       delete_after=5)
            amount_tracks = len(spotify_tracks)
            if amount_tracks > 1:
                msg = await i18n_emb_message(ctx, "PLAY-COMMAND-SPOTIFY-PROCESSING", colour=disnake.Colour.yellow())
                for t in spotify_tracks:
                    data = await self.get_video_data(f"ytsearch:{t[0]}")
                    if not data:
                        continue
                    self.add_to_queue(ctx, locale, data.get("entries")[0], [t[1], amount_tracks])
                await msg.delete()
            else:
                data = await self.get_video_data(f"ytsearch:{spotify_tracks[0]}")
                self.add_to_queue(ctx, locale, data.get("entries")[0])
        else:
            if playlist_count > 1:
                msg = await i18n_emb_message(ctx, "PLAY-COMMAND-YOUTUBE-PROCESSING", colour=disnake.Colour.yellow())
                data = await self.get_playlist_data(url, playlist_count)
                await msg.delete()
            else:
                data = await self.get_video_data(url)

            entries = data.get("entries")
            if entries and len(entries) > 1:
                for data in entries:
                    self.add_to_queue(ctx, locale, data, [data.get("playlist_index"), data.get("n_entries")])
            elif entries:
                self.add_to_queue(ctx, locale, data.get("entries"))
            else:
                self.add_to_queue(ctx, locale, data)

        if vc.is_playing() or vc.is_paused():
            await i18n_emb_message(ctx, "PLAY-COMMAND-ADD_LIST", False, f"{self.queues[guild_id][-1]['title']}",
                                   colour=disnake.Colour.green(),
                                   delete_after=2)
            return

        self.play_audio(ctx)

    @play.error
    async def play_error(self, ctx, error):
        try:
            lang = self.get_song_list(ctx.guild.id).pop(0)[0]['author_lang']
        except:
            lang = "en-US"
        if isinstance(error, AttributeError):
            emb_err = disnake.Embed(title='AttributeError',
                                    description=f'**{get_i18n_value("PLAY-COMMAND-ERROR-GUILD", lang)}**',
                                    colour=disnake.Colour.red())
        elif isinstance(error, ExtractorError):
            emb_err = disnake.Embed(title='ExtractError',
                                    description=f'{get_i18n_value("PLAY-COMMAND-ERROR_EMBED-DESCRIPTION1", lang)}\n'
                                                f'{get_i18n_value("PLAY-COMMAND-ERROR_EMBED-DESCRIPTION2", lang)}\n'
                                                f'```{error}```',
                                    colour=disnake.Colour.red())
        elif isinstance(error, DownloadError):
            emb_err = disnake.Embed(title='DownloadError',
                                    description=f'{get_i18n_value("PLAY-COMMAND-ERROR_EMBED-DESCRIPTION1", lang)}\n'
                                                f'{get_i18n_value("PLAY-COMMAND-ERROR_EMBED-DESCRIPTION2", lang)}\n'
                                                f'```{error}```',
                                    colour=disnake.Colour.red())
        else:
            emb_err = disnake.Embed(title='UnknownError',
                                    description=f'```{error}```',
                                    colour=disnake.Colour.red())
        emb_err.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar)
        await ctx.send(embed=emb_err, ephemeral=True)
        print(error)


def setup(bot):
    bot.add_cog(MusicCommands(bot))
