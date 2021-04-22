import discord
from discord.ext import commands
from datetime import datetime
import aiohttp
import traceback
import logging
import os
from asyncpg import Pool
from analyst.cache import BotCache

logger = logging.getLogger(__name__)


def loadall(bot):
    logger.info("Loading all the cogs")
    bot.load_extension("jishaku")
    for ext in os.listdir("./cogs/"):
        if ext == "__pycache__":
            continue
        try:
            logger.info(f"Loading {ext} ")
            bot.load_extension(f"cogs.{ext[:len(ext)-3]}")
        except Exception as e:
            logger.error(
                f"Failed to load {ext} !! Traceback saved in errors/{ext}.. {e}"
            )


async def get_prefix(bot, message):
    if message.guild.id in bot.cache.prefix.keys():
        return commands.when_mentioned_or(bot.cache.prefix[message.guild.id]["prefix"])(
            bot, message
        )

    async with bot.db.acquire() as conn:
        async with conn.transaction():
            gdata = await conn.fetchrow(
                "SELECT prefix FROM guilds WHERE gid=$1;", message.guild.id
            )
            bot.cache.prefix[message.guild.id]["prefix"] = gdata["prefix"]
    return commands.when_mentioned_or(gdata["prefix"])(bot, message)


class CEmbed(discord.Embed):
    def __init__(self, colorful=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = datetime.now()
        self.color = 0x2F3136
        if colorful:
            self.set_image(
                url="https://cdn.discordapp.com/attachments/616315208251605005/616319462349602816/Tw.gif"
            )


class Analyst(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embed = CEmbed
        self.db: Pool = kwargs.get("db")
        self.dev_guild = kwargs.get("dev_guild")
        self.error_channel = kwargs.get("error_channel")
        self.command_prefix = get_prefix
        self.cache = BotCache()
        self.cache["prefix"] = {}
        self.cache["guilds"] = {}
        self.config = kwargs.get("config")
        self.loop.create_task(self.cache_everything())
        self.logger = logger

    async def cache_everything(self):
        async with self.db.acquire() as conn:
            async with conn.transaction():
                gdata = await conn.fetch(
                    "SELECT prefix, gid FROM guilds;"
                )
        for row in gdata:
            self.cache.prefix[row["gid"]] = {"prefix": row["prefix"]}

    async def on_command_error(self, ctx, exc):
        if hasattr(ctx.command, "on_error"):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (
            commands.CommandNotFound,
            commands.MissingRequiredArgument,
            commands.MissingPermissions,
            commands.NotOwner,
        )

        error = getattr(exc, "original", exc)
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f"{ctx.command} has been disabled.")
            return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    f"{ctx.command} can not be used in Private Messages."
                )
                return
            except discord.HTTPException:
                pass

        error = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        async with aiohttp.ClientSession() as session:
            paste = await session.post("https://just-paste.it/documents", data=error)
            paste = await paste.json()
            async with self.db.acquire() as conn:
                async with conn.transaction():
                    id = await self.db.fetchrow(
                        "INSERT INTO  errors(url, type, fixed) VALUES($1, $2, false) RETURNING id, url;",
                        paste["key"],
                        type(exc).__name__,
                    )

        await ctx.send(
            embed=self.embed(
                title="Damn Error",
                description=f"An error has poped up. It has been reported to the shahad!!",
            )
        )
        channel = self.get_channel(int(self.error_channel))
        await channel.send(
            embed=self.embed(
                title="Error !!",
                description=f"An error has been registered with id {dict(id)['id']} and has been uploaded [here]({'https://just-paste.it/'+dict(id)['url']})",
            )
        )
