import asyncio
import typing
import asyncspotify
import discord
import re
import wavelink
import async_timeout
from discord.ext import commands
from wavelink.node import Node
from discord.ext import tasks
from asyncspotify import Client, ClientCredentialsFlow

URL_REGEX = re.compile(r"https?://(?:www\.)?.+")
TRACK_REGEX = re.compile(r"https://open\.spotify\.com/track/(\S+)\?si=\S*")
PLAYLIST_REGEX = re.compile(r"https://open\.spotify\.com/playlist/(\S+)\?si=\S*")


class CPlayer(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue()
        self.waiting = False
        self.ctx = kwargs.get("ctx")
        self.now_playing = None

    def build_embed(self, track):

        if isinstance(track, asyncspotify.FullPlaylist):
            embed = discord.Embed(
                colour=0xFFD105, title=f"Playlist - {track.name}", url=track.link
            )
            embed.add_field(
                name="Queued", value=f"{len(track.tracks)+self.queue.qsize()} songs"
            )
            if image := track.images[0]:
                embed.set_thumbnail(url=image.url)

        elif isinstance(track, asyncspotify.FullTrack):
            embed = discord.Embed(colour=0xFFD105, title=track.name, url=track.link)
            embed.add_field(name="Artists", value=" ,".join([artist.name for artist in track.artists]))
            embed.add_field(name="Queued", value=f"{self.queue.qsize()} songs")
            embed.add_field(
                name="Duration",
                value=f"{str(round(track.duration.seconds/60, 2)).replace('.', ':')} min(s)",
            )
            if image := track.album.images[0]:
                embed.set_thumbnail(url=image.url)

        elif isinstance(track, wavelink.TrackPlaylist):
            embed = discord.Embed(
                colour=0xFFD105, title=track.data["playlistInfo"]["name"]
            )
            embed.add_field(
                name="Queued", value=f"{len(track.tracks)+self.queue.qsize()} songs"
            )

        else:
            embed = discord.Embed(colour=0xFFD105, title=track.title, url=track.uri)
            embed.add_field(name="Publisher", value=track.author)
            embed.add_field(name="Queued", value=f"{self.queue.qsize()} songs")
            embed.add_field(
                name="Duration",
                value=f"{str(round(track.duration/60000, 2)).replace('.', ':')} min(s)",
            )
            embed.set_thumbnail(url=track.thumb)

        return embed

    async def play_next(self):
        if self.is_playing or self.waiting:
            return

        try:
            self.waiting = True
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            return await self.ctx.send(
                embed=discord.Embed(
                    color=0xFFD105,
                    description="No music in Queue! Play something, I'm bored..",
                )
            )

        self.waiting = False
        if isinstance(track, str):
            track = await self.ctx.bot.wavelink.get_tracks(query=track)
            track = track[0]

        if not track:
            await self.stop()
            return await self.ctx.send(embed=discord.Embed(color=0xFFD105, description="Track not found! Skipping!!"))

        await self.play(track)
        self.now_playing = track
        await self.ctx.send(embed=self.build_embed(track), delete_after=20)


class Music(commands.Cog, wavelink.WavelinkMixin):
    """Music Cog."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emoji = 836841369565134858
        bot.loop.create_task(self.connect_node())

    async def connect_node(self):
        # Why here? This is here to stop aiohttp whining about initializing in a non async function
        if not hasattr(self.bot, "wavelink"):
            self.bot.wavelink = wavelink.Client(bot=self.bot)
        self.wavelink: wavelink.Client = self.bot.wavelink

        await self.bot.wait_until_ready()

        config = self.bot.config
        if not "MAIN" in self.wavelink.nodes:
            await self.bot.wavelink.initiate_node(
                host=config.LAVALINK_IP,
                port=config.LAVALINK_PORT,
                rest_uri=f"http://{config.LAVALINK_IP}:{config.LAVALINK_PORT}",
                password=config.LAVALINK_PASS,
                identifier="MAIN",
                region="india",
            )
            self.sauth = ClientCredentialsFlow(
                client_id=config.SPOTIFY_ID,
                client_secret=config.SPOTIFY_SECRET,
            ) 

        self.check_dead_vc.start()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param == "Voice Channel":
                return await ctx.reply("Please specify a voice channel or join on!")

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: Node):
        self.bot.logger.info(f"Music: {node.identifier} is Ready")

    @tasks.loop(minutes=5)
    async def check_dead_vc(self):
        for player in self.wavelink.players.values():
            members = self.bot.get_channel(player.channel_id).members 
            if members and len(members) == 1:
                await player.ctx.send(
                    embed=discord.Embed(
                        color=0xFFD105,
                        description="Leaving voice channel!! No one was listening to my sweet music :(",
                    ),
                    delete_after=10,
                )
                await player.destroy()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel = before.channel or after.channel
        player = self.wavelink.get_player(channel.guild.id, cls=CPlayer)

        if member == self.bot.user and not after.channel:
            await player.destroy()

        if member == self.bot.user:
            if not after.deaf:
                await member.edit(deafen=True)

    @wavelink.WavelinkMixin.listener(event="on_track_exception")
    @wavelink.WavelinkMixin.listener(event="on_track_stuck")
    @wavelink.WavelinkMixin.listener(event="on_track_end")
    async def handle_track_end(self, node: Node, payload):
        player = payload.player
        if isinstance(payload, wavelink.TrackStuck) or isinstance(
            payload, wavelink.TrackException
        ):
            if player.queue.empty():
                await player.ctx.send(
                    embed=discord.Embed(
                        color=0xFFD105,
                        title="Error",
                        description="Something wrong happened to the track, This has been reported to the dev! Please try again",
                    )
                )
            else:
                await player.ctx.send(
                    embed=discord.Embed(
                        color=0xFFD105,
                        title="Error",
                        description="Something wrong happened to the track, This has been reported to the dev! Skipping to the next song!",
                    )
                )
                await player.play_next()

        else:
            await player.play_next()

    @commands.command(alias=["c"])
    async def connect(self, ctx, channel: typing.Optional[discord.VoiceChannel] = None):
        player = self.wavelink.get_player(ctx.guild.id, cls=CPlayer, ctx=ctx)

        if player.is_connected:
            return

        channel = getattr(ctx.author.voice, "channel", channel)
        if not channel:
            raise commands.MissingRequiredArgument("Voice Channel")

        await ctx.send(
            embed=discord.Embed(color=0xFFD105, description=f"Joining {channel.name}"),
            delete_after=10,
        )
        await player.connect(channel.id)
        await ctx.me.edit(deafen=True)

    @commands.command(alias=["p"])
    async def play(self, ctx, *, search: str):
        player = self.wavelink.get_player(ctx.guild.id, cls=CPlayer, ctx=ctx)
        playlist = None
        if not player.is_connected:
            await ctx.invoke(self.connect)

        if URL_REGEX.match(search):
            if track := TRACK_REGEX.match(search):

                async with Client(self.sauth) as sess:
                    try:
                        track = await sess.get_track(track.group(1))
                        await player.queue.put(f"ytsearch:{track.name} by {' '.join([author.name for author in track.artists])}")
                    except asyncspotify.exceptions.NotFound:
                        return await ctx.send(embed=discord.Embed(color=0xFFD105, description="Requested spotify playlist not found!"))

            elif tracks := PLAYLIST_REGEX.match(search):

                async with Client(self.sauth) as sess:
                    try:
                        playlist = await sess.get_playlist(tracks.group(1))
                        async for track in playlist:
                            await player.queue.put(f"ytsearch:{track.name} by {' '.join([author.name for author in track.artists])}")
                        await ctx.send(embed=player.build_embed(playlist), delete_after=20)
                    except asyncspotify.exceptions.NotFound:
                        return await ctx.send(embed=discord.Embed(color=0xFFD105, description="Requested spotify playlist not found!"))

            elif tracks := await self.wavelink.get_tracks(query=search):

                if isinstance(tracks, wavelink.TrackPlaylist):
                    for track in tracks.tracks:
                        await player.queue.put(track)
                    await ctx.send(embed=player.build_embed(tracks), delete_after=20)
                else:
                    await player.queue.put(tracks[0])

        elif not URL_REGEX.match(search):
            search = f"ytsearch:{search}"
            track = await self.wavelink.get_tracks(query=search)
            await player.queue.put(track[0])
            if player.is_playing:
                await ctx.send(embed=player.build_embed(track[0]), delete_after=20)

        if not player.is_playing:
            await player.play_next()

    @commands.command(alias=["s"])
    async def skip(self, ctx):
        player = self.wavelink.get_player(ctx.guild.id, cls=CPlayer, ctx=ctx)
        await player.stop()
        await ctx.send(
            embed=discord.Embed(color=0xFFD105, description="Skipping !"),
            delete_after=10,
        )

    @commands.command()
    async def pause(self, ctx):
        player = self.wavelink.get_player(ctx.guild.id, cls=CPlayer, ctx=ctx)
        await player.set_pause(True)
        await ctx.send(
            embed=discord.Embed(color=0xFFD105, description="Pausing Player"),
            delete_after=10,
        )

    @commands.command(alias=["v"])
    async def volume(self, ctx, amount: int):
        player = self.wavelink.get_player(ctx.guild.id, cls=CPlayer, ctx=ctx)
        await player.set_volume(amount)
        await ctx.send(
            embed=discord.Embed(color=0xFFD105, description=f"Volume set to {amount}"),
            delete_after=10,
        )

    @commands.command(alias=["dc", "stop"])
    async def leave(self, ctx):
        player = self.wavelink.get_player(ctx.guild.id, cls=CPlayer, ctx=ctx)
        await player.destroy()
        await ctx.send(
            embed=discord.Embed(color=0xFFD105, description=f"Leaving the VC! Bye Bye"),
            delete_after=10,
        )

    @commands.command(alias=["continue"])
    async def resume(self, ctx):
        player = self.wavelink.get_player(ctx.guild.id, cls=CPlayer, ctx=ctx)
        await player.set_pause(False)
        await ctx.send(
            embed=discord.Embed(color=0xFFD105, description="Resuming Player"),
            delete_after=10,
        )


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
