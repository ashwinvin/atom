import typing
from discord.ext import commands
import discord


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, users: commands.Greedy[discord.Member], *reason: str):
        try:
            for user in users:
                await user.ban(reason="".join(reason))
            await ctx.send(
                f"Banned {''.join([f'**{a.name}#{a.discriminator}**' for a in users])} \n Reason {''.join(reason)}"
            )
        except discord.Forbidden:
            await ctx.send(f"Looks like I don't have the Permission to do that :(")

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, users: commands.Greedy[discord.Member], *reason: str):
        try:
            for user in users:
                await user.kick(reason="".join(reason))
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
                member = discord.Object(id=user)  # user ID
                try:
                    await ctx.guild.unban(user=member)
                except discord.NotFound:
                    check = discord.utils.find(
                        lambda member: member.id == user, ctx.guild.members
                    )
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


def setup(bot):
    bot.add_cog(Moderation(bot))
