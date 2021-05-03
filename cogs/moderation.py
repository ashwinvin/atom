import math
import typing

import discord
from discord.ext import commands


class Moderation(commands.Cog, name="Moderation", description="Module for server moderation"):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = 836839655789822012

    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, users: commands.Greedy[discord.Member], *reason: str):
        try:
            for user in users:
                await user.ban(reason="".join(reason))
            await ctx.send(f"Banned {''.join([f'**{a.name}#{a.discriminator}**' for a in users])} \n Reason {''.join(reason)}")
        except discord.Forbidden:
            await ctx.send(f"Looks like I don't have the Permission to do that :(")

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, users: commands.Greedy[discord.Member], *reason: str):
        try:
            for user in users:
                await user.kick(reason="".join(reason))
            await ctx.send(f"Kicked {[f'**{a.name}#{a.discriminator}**' for a in users]} \n Reason {''.join(reason)}")
        except discord.Forbidden:
            await ctx.send(f"Looks like I don't have the Permission to do that :(")

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, users: commands.Greedy[int]):
        try:
            for user in users:
                member = discord.Object(id=user)  # user ID
                try:
                    await ctx.guild.unban(user=member)
                except discord.NotFound:
                    check = discord.utils.find(lambda member: member.id == user, ctx.guild.members)
                    if check:
                        await ctx.send(f"{check.mention} is not banned!")
            await ctx.send(f"Unbanned {''.join([f'**{a.name}#{a.discriminator}**' for a in users])}")
        except discord.Forbidden:
            await ctx.send(f"Looks like I don't have the Permission to do that :(")

    @commands.command(help="Used to lock a channel")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        roles = ctx.guild.roles
        if not channels:
            channels = [ctx.channel]
        for channel in channels:
            lock_embed = self.bot.embed(
                title="Locked",
                description=f"This channel is locked by {ctx.message.author}",
                color=0xEB984E,
            )
            await channel.send(embed=lock_embed)
            for role in roles:
                await channel.set_permissions(role, send_messages=False, reason=f"Done by {ctx.message.author}")

    @commands.command(help="Used to unlock a channel after its been locked")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        roles = ctx.guild.roles
        if not channels:
            channels = [ctx.channel]
        for channel in channels:
            lock_embed = self.bot.embed(
                title="Unlocked",
                description=f"This channel is now unlocked by {ctx.message.author}",
                color=0xEB984E,
            )
            await channel.send(embed=lock_embed)

            for role in roles:
                await channel.set_permissions(role, send_messages=True, reason=f"Done by {ctx.message.author}")

    @commands.command(help="Set slowmode for a channel")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, channel: typing.Optional[discord.TextChannel], time: int):
        if time > 21600:
            return await ctx.send("Time cannot be greater than 21600")
        if not channel:
            channel = ctx.channel
        await channel.edit(slowmode_delay=time)
        await ctx.send(f"Slowmode for {channel.mention} is now {time} seconds")

    @commands.command(help="")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def nuke(self, ctx):
        def checkM(msg):
            return ctx.author == msg.author and msg.channel == ctx.channel

        await ctx.reply("This command will delete all the messages in this channel. Reply `Y` if you still want to continue")
        consent = await self.bot.wait_for("message", check=checkM)

        if not consent.content in ["Y", "y"]:
            try:
                return await ctx.reply("Nuking aborted")
            except commands.MessageNotFound:
                return await ctx.send("Nuking aborted")

        await ctx.channel.clone(reason=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
        await ctx.channel.delete(reason=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")

    @commands.group()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def purge(self, ctx: commands.Context, messages: int):
        rem, actual = messages % 100, math.floor(messages / 100)
        i = 0
        cleaned = 0
        try:
            while i < actual:
                cleaned += len(await ctx.channel.purge(limit=rem, bulk=True))
        except discord.Forbidden:
            pass
        await ctx.send(f"Purged {cleaned} messages!")

    @purge.command()
    async def bots(self, ctx: commands.Context, messages: int):
        rem, actual = messages % 100, math.floor(messages / 100)
        i = 0
        cleaned = 0
        try:
            while i < actual:
                cleaned += len(await ctx.channel.purge(limit=rem, bulk=True, check=lambda m: m.author.bot))
        except discord.Forbidden:
            pass
        await ctx.send(f"Purged {cleaned} messages!")

    @purge.command()
    async def users(self, ctx: commands.Context, messages: int):
        rem, actual = messages % 100, math.floor(messages / 100)
        i = 0
        cleaned = 0
        try:
            while i < actual:
                cleaned += len(await ctx.channel.purge(limit=rem, bulk=True, check=lambda m: not m.author.bot))
        except discord.Forbidden:
            pass
        await ctx.send(f"Purged {cleaned} messages!")


def setup(bot):
    bot.add_cog(Moderation(bot))
