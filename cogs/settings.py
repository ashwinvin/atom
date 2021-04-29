import discord
from discord.ext import commands


class Settings(
    commands.Cog, description="Handles the bot's configuration for this server"
):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = 836842746337165344

    async def cog_check(self, ctx):
        if not ctx.guild:
            await ctx.send("This command should be run inside a server!!")
            return False

        if not ctx.author.guild_permissions.administrator:
            await ctx.send("This command is restricted to admins!!")
            return False

        return True

    @commands.group()
    async def config(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.reply(
                embed=self.bot.embed(
                    description=f"Use `{ctx.prefix}config set` for setting up config values \n \
                        Use `{ctx.prefix}config reset` to reset entire server config.",
                    colorful=False,
                )
            )

    @config.group()
    async def set(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.reply(
                embed=self.bot.embed(
                    description=f"Use `{ctx.prefix}config set samp <ip> <port>` for setting samp config \n \
                        Use `{ctx.prefix}config set mc <ip> <port>` for setting minecraft config. \n \
                        Use `{ctx.prefix}config set prefix`  to set custom prefix",
                    colorful=False,
                )
            )

    @config.command()
    async def reset(self, ctx: commands.Context):
        await ctx.send("Reset all the configs for this server....")
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM guilds WHERE gid = $1;", ctx.guild.id)
                await conn.execute("INSERT INTO guilds(gid) VALUES($1);", ctx.guild.id)
                guild = await self.bot.cache.get(ctx.guild.id)
                guild = guild._replace(
                    prefix=self.bot.config.PREFIX,
                    minecraft={"ip": None, "port": None},
                    samp={"ip": None, "port": None},
                )
                await self.bot.cache.set(ctx.guild.id, guild)
        await ctx.send("Done!")

    @set.command()
    async def samp(self, ctx: commands.Context, ip: str, port: int):
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                id = await conn.execute(
                    """INSERT INTO samp(id, samp_ip, samp_port)
                            VALUES((SELECT guilds.id FROM guilds WHERE gid = $3), $1, $2)
                            ON CONFLICT (id) DO
                            UPDATE SET samp_ip=$1 , samp_port=$2 WHERE samp.id = (SELECT id FROM guilds WHERE gid = $3);""",
                    ip,
                    port,
                    ctx.guild.id,
                )
                guild = await self.bot.cache.get(ctx.guild.id)
                guild = guild._replace(samp={"ip": ip, "port": port})
                await self.bot.cache.set(ctx.guild.id, guild)
        await ctx.reply(
            embed=self.bot.embed(
                description=f"Samp Server info has been updated!!", colorful=True
            )
        )

    @set.command()
    async def mc(self, ctx: commands.Context, ip: str, port: int):
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """INSERT INTO minecraft(id, mc_ip, mc_port)
                            VALUES((SELECT guilds.id FROM guilds WHERE gid = $3), $1, $2)
                            ON CONFLICT (id) DO
                            UPDATE SET mc_ip=$1 , mc_port=$2 WHERE minecraft.id = (SELECT id FROM guilds WHERE gid = $3);""",
                    ip,
                    port,
                    ctx.guild.id,
                )
                guild = await self.bot.cache.get(ctx.guild.id)
                guild = guild._replace(minecraft={"ip": ip, "port": port})
                await self.bot.cache.set(ctx.guild.id, guild)

        await ctx.reply(
            embed=self.bot.embed(
                description=f"Samp Server info has been updated!!", colorful=True
            )
        )

    @set.command()
    async def prefix(self, ctx: commands.Context, prefix: str):
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE guilds SET prefix=$1 WHERE gid=$2;", prefix, ctx.guild.id
                )
                guild = await self.bot.cache.get(ctx.guild.id)
                guild = guild._replace(prefix=prefix)
                await self.bot.cache.set(ctx.guild.id, guild)
        return await ctx.send(f"Prefix is now `{prefix}`")


def setup(bot):
    bot.add_cog(Settings(bot))
