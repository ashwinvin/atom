import discord
from samp_client.client import SampClient
from discord.ext.commands.cooldowns import BucketType
from discord.ext import menus
from discord.ext import commands
import statistics
import functools


def get_samp_data(ip: str, port: int):
    with SampClient(address=ip, port=port) as client:
        players = client.get_server_clients_detailed()
        server_info = client.get_server_info()
        return players, server_info

class SampPlayers(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=15)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        return discord.Embed(title="Samp Players", description='\n'.join(f'{i}. {v.name}  `ping {v.ping}ms` ' for i, v in enumerate(entries, start=offset)))



class SampUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def samp(self, ctx):
        if not ctx.invoked_subcommands:
            await ctx.reply(
                embed=self.bot.embed(
                    description=f"Use `{ctx.prefix}samp players` for player info \n Use `{ctx.prefix}samp info` for general info", colorful=False
                )
            )

    async def get_samp_ip_port(self, id):
        async with self.db.acquire() as conn:
            async with conn.transaction():
                gdata = await conn.fetchrow("SELECT samp_port, samp_ip FROM guilds WHERE gid=$1;", id)
        return gdata

    @commands.has_permissions(administrator=True)
    @samp.command(name="set samp", ignore_extra=True)
    async def set(self, ctx, ip: str, port: int):
        async with self.db.acquire() as conn:
            async with conn.transaction():
                id = await self.db.execute(
                    "INSERT INTO  guilds(samp_ip, samp_url) VALUES($1, $2) WHERE gid=$3 ON CONFLICT DO UPDATE SET samp_ip=$1, samp_port=$2 WHERE gid=$3;",
                    ip,
                    port,
                    ctx.guild.id,
                )
        await ctx.reply(
            embed=self.bot.embed(
                description=f"Samp Server info has been updated!!", colorful=True
            )
        )

    @commands.cooldown(1, 3, BucketType.guild)
    @samp.command()
    async def info(self, ctx):
        async with ctx.typing():
            gdata = self.get_samp_ip_port(ctx.guild.id)
            request = functools.partial(get_samp_data, gdata['samp_ip'],gdata['samp_port'])
            results = await self.bot.loop.run_in_executor(None, request)
            embed = self.bot.embed(title="Samp Status", description=f"```{results.hostname}```", colorful=False)
            embed.add_field(name="Players", value=f"{len(results[1])} Players Online")
            embed.add_field(name="Average Ping", value=f"{int(statistics.mean([a.ping for a in results[1]]))} ms")
            await ctx.reply(embed=embed)

    @commands.cooldown(1, 3, BucketType.guild)
    @samp.command()
    async def players(self, ctx):
        async with ctx.typing():
            gdata = self.get_samp_ip_port(ctx.guild.id)
            request = functools.partial(get_samp_data, gdata['samp_ip'], gdata['samp_port'])
            results = await self.bot.loop.run_in_executor(None, request)
            players = [a for a in results]
            # embed = self.bot.embed(title="Samp Players", description=f"```{results.hostname}```", colorful=False)
            menus = menus.MenuPages(source=SampPlayers(players), clear_reactions_after=True)
            await menus.start(ctx)

def setup(bot):
    bot.add_cog(SampUtils(bot))