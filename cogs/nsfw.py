import aiohttp
from discord.ext import commands

class Nsfw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.bot.loop.create_task(self.initialize())

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    def cog_check(self, ctx: commands.Context):
        if ctx.channel.is_nsfw():
           return True
        return False

    @commands.command()
    async def waifu(self, ctx):
        async with ctx.typing():
            async with self.session.get("https://waifu.pics/api/nsfw/waifu") as resp:
                data = await resp.json()
                if resp.status != 200:
                    return await ctx.send(embed=self.bot.embed(description="The API is not responding!! Try again later"))
                embed=self.bot.embed(title="Here is a Waifu for you")
                embed.set_image(url=data["url"])
                await ctx.reply(embed=embed)

    @commands.command()
    async def neko(self, ctx):
        async with ctx.typing():
            async with self.session.get("https://waifu.pics/api/nsfw/neko") as resp:
                data = await resp.json()
                if resp.status != 200:
                    return await ctx.send(embed=self.bot.embed(description="The API is not responding!! Try again later"))
                embed=self.bot.embed(title="Here is a Neko for you")
                embed.set_image(url=data["url"])
                await ctx.reply(embed=embed)

    @commands.command(aliases=["bj"])
    async def blowjob(self, ctx):
        async with ctx.typing():
            async with self.session.get("https://waifu.pics/api/nsfw/blowjob") as resp:
                data = await resp.json()
                if resp.status != 200:
                    return await ctx.send(embed=self.bot.embed(description="The API is not responding!! Try again later"))
                embed=self.bot.embed(title="Here is a Blowjob pic for you")
                embed.set_image(url=data["url"])
                await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(Nsfw(bot))