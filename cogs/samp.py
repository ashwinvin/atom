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
        embed = discord.Embed(title="Samp Players", description='\n'.join(f'{i}. {v.name}  `ping {v.ping}ms` ' for i, v in enumerate(entries, start=offset)), color=0x2F3136)
        embed.set_footer(text="Shahad Uyir")
        return embed


class SampUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def samp(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.reply(
                embed=self.bot.embed(
                    description=f"Use `{ctx.prefix}samp players` for player info \n Use `{ctx.prefix}samp info` for general info", colorful=False
                )
            )

    async def get_samp_ip_port(self, id):
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                gdata = await conn.fetchrow("SELECT samp_ip,samp_port  FROM guilds INNER JOIN samp ON guilds.id = samp.id WHERE gid = $1;", id)
        return gdata

    @commands.has_permissions(administrator=True)
    @samp.command(ignore_extra=True)
    async def set(self, ctx, ip: str, port: int):
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
        await ctx.reply(
            embed=self.bot.embed(
                description=f"Samp Server info has been updated!!", colorful=True
            )
        )
        
    @commands.cooldown(1, 3, BucketType.guild)
    @samp.command()
    async def info(self, ctx):
        async with ctx.typing():
            gdata = await self.get_samp_ip_port(ctx.guild.id)
            if not gdata:
                return await ctx.reply(embed=self.bot.embed(description=f"Samp module is not configured.. Pls do `{ctx.prefix}samp set ip port`", colorful=False))
            request = functools.partial(get_samp_data, gdata['samp_ip'],gdata['samp_port'])
            try:
                results = await self.bot.loop.run_in_executor(None, request)
            except Exception as e:
                return await ctx.reply(embed=self.bot.embed(description="Seems like the server is down!", colorful=False))
            embed = self.bot.embed(title="Samp Status", description=f"```{results[1].hostname}```", colorful=False)
            embed.add_field(name="Players", value=f"{len(results[0])} Players Online")
            embed.add_field(name="Average Ping", value=f"{int(statistics.mean([a.ping for a in results[0]]))} ms")
            embed.set_footer(text="Shahad Uyir")
            await ctx.reply(embed=embed)

    @commands.cooldown(1, 3, BucketType.guild)
    @samp.command()
    async def players(self, ctx):
        async with ctx.typing():
            gdata = await self.get_samp_ip_port(ctx.guild.id)
            if not gdata:
                return await ctx.reply(embed=self.bot.embed(description=f"Samp module is not configured.. Pls do `{ctx.prefix}samp set ip port`", colorful=False))
            request = functools.partial(get_samp_data, gdata['samp_ip'], gdata['samp_port'])
            try:
                results = await self.bot.loop.run_in_executor(None, request)
            except Exception as e:
                return await ctx.reply(embed=self.bot.embed(description="Seems like the server is down!", colorful=False))
            players = [a for a in results[0]]
            smenus = menus.MenuPages(source=SampPlayers(players), clear_reactions_after=True)
            await smenus.start(ctx)

def setup(bot):
    bot.add_cog(SampUtils(bot))