import asyncio
import typing
import aiohttp
from io import BytesIO
import discord
from yarl import URL
from discord.ext import commands


class GuildManagement(
    commands.Cog,
    name="Server Management",
    description="Module for managing everyday server events",
):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = 836843090870272020

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute("INSERT INTO guilds(gid) VALUES($1)", guild.id)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def poll(self, ctx, description: str, choice1: str, choice2: str):
        """ """
        description = f"{description} \n \n \U0001f170 {choice1} \n \U0001f171 {choice2}"
        poll_embed = self.bot.embed(
            title="Poll",
            color=0x77FC03,
            description="".join(description),
            colorful=False,
        )
        poll_embed.set_footer(text=f"Poll started by {ctx.author.name}")
        msg = await ctx.send(embed=poll_embed)
        await msg.add_reaction("\U0001f170")
        await msg.add_reaction("\U0001f171")

    @commands.command()
    async def bots(self, ctx):
        description = ""
        for member in ctx.guild.members:
            if member.bot:
                description += f"{member.mention} joined at {str(member.joined_at.strftime('%Y:%m:%d'))} \n"
                pass

        embed = self.bot.embed(title=f"Bots in {ctx.guild.name}", description=description)
        await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.group(invoke_without_command=True)
    async def emoji(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help("emoji")

    @emoji.command()
    async def add(
        self,
        ctx: commands.Context,
        name: str,
        stolen_emoji: typing.Optional[discord.PartialEmoji],
        url: typing.Optional[str],
        roles: commands.Greedy[discord.Role],
    ):

        sess = aiohttp.ClientSession()

        async def add_emoji(url, name):
            async with sess.get(url) as resp:
                emoji = await ctx.guild.create_custom_emoji(name=name, image=await resp.read(), roles=roles)
                return await ctx.reply(f"{emoji} has been added")

        # if not URL(url).scheme:
        #     return await ctx.reply("The provided url is not valid")

        if url:
            await add_emoji(url, name)
        elif ctx.message.attachments:
            await add_emoji(ctx.message.attachments[0].url, name)
        elif stolen_emoji:
            await add_emoji(f"https://cdn.discordapp.com/emojis/{emoji.id}.png?v=1", name)
        else:
            await ctx.reply("No attachment or url provided!!")
        return await sess.close()

    @emoji.command()
    async def delete(self, ctx, emojis: commands.Greedy[discord.Emoji]):
        def checkM(msg):
            return ctx.author == msg.author and msg.channel == ctx.channel

        await ctx.reply("This command will delete emojis permanently. Reply `Y` if you still want to continue")
        consent = await self.bot.wait_for("message", check=checkM)

        if not consent.content in ["Y", "y"]:
            try:
                return await ctx.reply("Deletion Aborted")
            except commands.MessageNotFound:
                return await ctx.send("Deletion Aborted")

        status = await asyncio.gather(*[emoji.delete() for emoji in emojis], return_exceptions=True)
        print(status)
        await ctx.reply(f"Successfully deleted {len(emojis)} emojis")


def setup(bot):
    bot.add_cog(GuildManagement(bot))
