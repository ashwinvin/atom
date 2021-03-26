import time
import discord
import typing
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
                description="Main API : {:.2f} ms \n Websocket {:.2f} ms".format(
                    duration, self.bot.latency * 1000
                ),
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
                    await ctx.send(
                        embed=self.bot.embed(
                            description=f"{cog} was not reloaded as it was not found"
                        )
                    )
        else:
            cogs = list(self.bot.extensions.keys())
            for cog in cogs:
                try:
                    self.bot.reload_extension(cog)
                    temp.append(cog)
                except commands.ExtensionNotFound:
                    await ctx.send(
                        embed=self.bot.embed(
                            description=f"{cog} was not reloaded as it was not found"
                        )
                    )
        description = ""
        await first.delete()
        for cog in temp:
            description += f"\n Reloaded {cog} <:on:824390304474857534>"
        if description != "":
            await ctx.send(embed=self.bot.embed(description=description))
        else:
            await ctx.send(
                embed=self.bot.embed(
                    description="Failed to reload Cogs!! \n Check console for errors"
                )
            )


def setup(bot):
    bot.add_cog(DevTools(bot))
