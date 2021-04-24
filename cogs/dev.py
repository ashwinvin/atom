import asyncio
import time
import typing
import beautifultable
from discord.ext import commands


class DevTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def ping(self, ctx):
        start = time.perf_counter()
        message = await ctx.send(embed=self.bot.embed(title="Pong..."))
        end = time.perf_counter()
        duration = (end - start) * 1000
        await message.edit(
            embed=self.bot.embed(
                title="Ping Results",
                description="Main API : {:.2f} ms \n Websocket {:.2f} ms".format(duration, self.bot.latency * 1000),
            )
        )

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, *cogs: typing.Optional[str]):
        first = await ctx.send(embed=self.bot.embed(description="Reloading Cogs!"))
        temp = []
        if cogs:
            for cog in cogs:
                try:
                    self.bot.reload_extension(cog)
                    temp.append(cog)
                except commands.ExtensionNotFound:
                    await ctx.send(embed=self.bot.embed(description=f"{cog} was not reloaded as it was not found"))
        else:
            cogs = list(self.bot.extensions.keys())
            for cog in cogs:
                try:
                    self.bot.reload_extension(cog)
                    temp.append(cog)
                except commands.ExtensionNotFound:
                    await ctx.send(embed=self.bot.embed(description=f"{cog} was not reloaded as it was not found"))
        description = ""
        await first.delete()
        for cog in temp:
            description += f"\n <:on1:824388581433933896> Reloaded {cog} "
        if description != "":
            await ctx.send(embed=self.bot.embed(description=description))
        else:
            await ctx.send(embed=self.bot.embed(description="Failed to reload Cogs!! \n Check console for errors"))

    @commands.is_owner()
    @commands.command()
    async def sync(self, ctx):
        msg = await ctx.send(embed=self.bot.embed(description="Pulling from git"))
        proc = await asyncio.create_subprocess_shell(
            "git pull", stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await proc.communicate()
        except Exception as e:
            return await ctx.send(f"Something Happened! Failed to pull from git \n {e}")
        embed = self.bot.embed(
            description=f"Done! \n ```{stdout.decode('utf-8')}``` \n Process exited with code : {proc.returncode}"
        )
        await msg.edit(embed=embed)
        await ctx.invoke(self.reload)

    @commands.is_owner()
    @commands.command()
    async def sql(self, ctx, *query: str):
        try:
            async with self.bot.db.acquire() as conn:
                async with conn.transaction():
                    results = await conn.fetch(" ".join(query))
                    table = beautifultable.BeautifulTable()
                    if not results:
                        return await ctx.send("The SQL query returned nothing!! ")
                    table.columns.header = list(results[0].keys())
                    for result in results:
                        table.rows.append(result.values())
                    await ctx.send(f"```{table}```")
        except Exception as e:
            await ctx.send(f"Sql Statement failed due to \n {e}")


def setup(bot):
    bot.add_cog(DevTools(bot))
