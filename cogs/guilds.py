import discord
import typing
from datetime import datetime
import textwrap
from discord.ext import commands


class GManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, users: commands.Greedy[discord.Member], *reason: str):
        try:
            for user in users:
                await user.ban(reason=''.join(reason))
            await ctx.send(
                f"Banned {''.join([f'**{a.name}#{a.discriminator}**' for a in users])} \n Reason {''.join(reason)}"
            )
        except discord.Forbidden:
            await ctx.send(f"Looks like I don't have the Permission to do that :(")

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, users: commands.Greedy[discord.Member], *reason: str):
        try:
            for user in users:
                await user.kick(reason=''.join(reason))
            await ctx.send(
                f"Kicked {[f'**{a.name}#{a.discriminator}**' for a in users]} \n Reason {''.join(reason)}"
            )
        except discord.Forbidden:
            await ctx.send(f"Looks like I don't have the Permission to do that :(")

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.command()
    async def unban(self, ctx, users: commands.Greedy[int]):
        try:
            for user in users:
                member = discord.Object(id=user) # user ID
                try:
                    await ctx.guild.unban(user=member)
                except discord.NotFound:
                    check = discord.utils.find(lambda member: member.id == user, ctx.guild.members)
                    if check:
                        await ctx.send(f"{check.mention} is not banned!")
            await ctx.send(
                f"Unbanned {''.join([f'**{a.name}#{a.discriminator}**' for a in users])}"
            )
        except discord.Forbidden:
            await ctx.send(f"Looks like I don't have the Permission to do that :(")

    @commands.command(help="Used to lock a channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel):
        roles = ctx.guild.roles
        lock_embed = self.bot.embed(
            title="Locked",
            description=f"This channel is locked by {ctx.message.author}",
            color=0xEB984E,
        )
        await channel.send(embed=lock_embed)
        for role in roles:
            await channel.set_permissions(
                role, send_messages=False, reason=f"Done by {ctx.message.author}"
            )

    @commands.command(help="Used to unlock a channel after its been locked")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel):
        roles = ctx.guild.roles
        lock_embed = self.bot.embed(
            title="Locked",
            description=f"This channel is now unlocked by {ctx.message.author}",
            color=0xEB984E,
        )
        await channel.send(embed=lock_embed)

        for role in roles:
            await channel.set_permissions(
                role, send_messages=True, reason=f"Done by {ctx.message.author}"
            )

    @commands.command(help="Set slowmode for a channel")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(
        self, ctx, channel: typing.Optional[discord.TextChannel], time: int
    ):
        if time > 21600:
            return await ctx.send("Time cannot be greater than 21600")
        if not channel:
            channel = ctx.channel
        await channel.edit(slowmode_delay=time)
        await ctx.send(f"Slowmode for {channel.mention} is now {time} seconds")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def poll(
        self, ctx, channel: typing.Optional[discord.TextChannel], *description: str
    ):
        poll_embed = discord.Embed(
            title="Poll", color=0x008000, description=description
        )
        msg: discord.Message = await channel.send(embed=poll_embed)
        await msg.add_reaction("⬆️")
        await msg.add_reaction("⬇️")

    @commands.command()
    async def info(
        self,
        ctx: commands.Context,
        needed: typing.Optional[typing.Union[discord.Member, discord.Role]],
    ):
        if not needed:
            embed = self.bot.embed()
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.add_field(
                name="Owner",
                value=f"{ctx.guild.owner.name}#{ctx.guild.owner.discriminator}",
            )
            embed.add_field(name="Region", value=ctx.guild.region)
            embed.add_field(name="Members", value=ctx.guild.member_count)
            embed.add_field(
                name="Channels",
                value=f"Text Channels: {len(ctx.guild.text_channels)} \n Voice Channels{len(ctx.guild.voice_channels)}",
            )
            embed.add_field(
                name="Emojis", value="".join([str(a) for a in ctx.guild.emojis])
            )
            embed.add_field(name="Roles", value=len(ctx.guild.roles))
            embed.set_thumbnail(url=ctx.guild.icon_url)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GManagement(bot))
