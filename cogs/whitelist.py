import discord
from discord.ext import commands


class WhiteList(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def whitelist(self, ctx: commands.Context, user: discord.Member):
        pass
