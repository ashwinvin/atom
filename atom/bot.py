import glob
import hashlib
import logging
import traceback
from datetime import datetime

import aiohttp
import discord
from asyncpg import Pool
from discord.ext import commands

from atom.cache import BotCache, guildObject

logger = logging.getLogger(__name__)


def loadall(bot):
    logger.info("Loading all the cogs")
    bot.load_extension("jishaku")
    for ext in glob.glob("cogs/*.py"):
        try:
            logger.info(f"Loading {ext}")
            bot.load_extension(f"{ext[:len(ext)-3].replace('/','.')}")
        except Exception as e:
            logger.error(f"Failed to load {ext} !! Traceback saved in errors/{ext}.. {e}")


async def get_prefix(bot, message):
    if not message.guild:
        return commands.when_mentioned_or(bot.config.PREFIX)(bot, message)

    if await bot.cache.exists(message.guild.id):
        guild = await bot.cache.get(message.guild.id)
        return commands.when_mentioned_or(guild.prefix)(bot, message)

    async with bot.db.acquire() as conn:
        async with conn.transaction():
            gdata = await conn.fetchrow("SELECT prefix FROM guilds WHERE gid=$1;", message.guild.id)
            guild = await bot.cache.get(message.guild.id)
            guild = guild._replace(prefix=gdata["prefix"])
            await bot.cache.set(message.guild.id, guild)
    return commands.when_mentioned_or(gdata["prefix"])(bot, message)


class CEmbed(discord.Embed):
    def __init__(self, colorful=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = datetime.now()
        self.color = 0x2F3136
        if colorful:
            self.set_image(url="https://cdn.discordapp.com/attachments/616315208251605005/616319462349602816/Tw.gif")


class Atom(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embed = CEmbed
        self.db: Pool = kwargs.get("db")
        self.dev_guild = kwargs.get("dev_guild")
        self.error_channel = kwargs.get("error_channel")
        self.command_prefix = get_prefix
        self.config = kwargs.get("config")
        self.cache = BotCache(self.config)
        self.loop.create_task(self.cache_everything())
        self.logger = logger

    async def cache_everything(self):
        await self.wait_until_ready()
        await self.cache.clear()
        self.logger.info("Preparing to cache guild data")
        async with self.db.acquire() as conn:
            async with conn.transaction():
                # Gather all the data from db
                gdata = await conn.prepare(
                    "SELECT gid, prefix, samp_ip,samp_port, mc_port, mc_ip \
                    FROM guilds FULL JOIN samp ON guilds.id = samp.id \
                    FULL JOIN minecraft ON guilds.id = minecraft.id;"
                )
                guildIDs = [g.id for g in self.guilds]  # Create a guild id list for refrence
                async for row in gdata.cursor():
                    if row["gid"] in guildIDs:  # Remove the guild from list if it exists on th db
                        guildIDs.remove(row["gid"])
                    else:
                        await conn.execute("UPDATE SET kicked=$2 WHERE gid=$1", row["gid"], datetime.now())

                    await self.cache.add(
                        row["gid"],
                        guildObject(
                            row["prefix"],
                            {"samp_ip": row["samp_ip"], "samp_port": row["samp_port"]},
                            {"mc_ip": row["mc_ip"], "mc_port": row["mc_port"]},
                        ),
                    )

                if guildIDs:  # Check for new guilds
                    self.logger.info(f"New {len(guildIDs)} Guilds found!! Updating DB")
                    await conn.executemany("INSERT INTO guilds(gid) VALUES($1)", guildIDs)

                for ext in glob.glob("cogs/*.py"):
                    hash = hashlib.md5(str(open(ext).read()).encode("utf-8")).hexdigest()
                    await self.cache.add(ext, hash)

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
                await ctx.author.send(f"{ctx.command} can not be used in Private Messages.")
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
