import typing
import discord
from discord.ext import commands
import asyncio


class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.afkers = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id in self.afkers.keys():
            self.afkers.pop(message.author.id)
            await message.channel.send(
                embed=self.bot.embed(description=f"Welcome back {message.author.mention}", colorful=False)
            )
            try:
                await message.author.edit(nick=message.author.display_name[5:])
            except discord.Forbidden:
                await message.channel.send(
                    "Failed to change your nickname!! Permissions Denied!!",
                    delete_after=10,
                )
        if n := discord.utils.find(lambda n: n.id in self.afkers.keys(), message.mentions):
            await message.reply(
                embed=self.bot.embed(description=f"Sorry but `{n.display_name}` is afk \n Reason:```{self.afkers[n.id]}```")
            )

    @commands.command()
    async def afk(self, ctx, *reason: typing.Optional[str]):
        if not reason:
            reason = "Unknown"
        await ctx.send(
            embed=self.bot.embed(
                description=f"I have set your afk status to `{''.join(reason)}`",
                colorful=False,
            )
        )
        try:
            await ctx.author.edit(nick=f"[AFK]{ctx.author.display_name}")
        except discord.Forbidden:
            await ctx.send("Failed to change your nickname!! Permissions Denied!!", delete_after=10)
        await asyncio.sleep(2)
        self.afkers[ctx.author.id] = "".join(reason)

    @commands.guild_only()
    @commands.command(name="server-info")
    async def server_info(self, ctx):
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
        embed.add_field(name="Emojis", value=f"Total {len(ctx.guild.emojis)} emojis")
        embed.add_field(
            name="Boost Status",
            value=f"This Guild is boosted with {ctx.guild.premium_subscription_count} and has achieved level {ctx.guild.premium_tier} boost status"
            if ctx.guild.premium_subscribers
            else "This server is not boosted",
        )
        embed.add_field(name="Roles", value=len(ctx.guild.roles))
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(name="user-info")
    async def user_info(
        self,
        ctx: commands.Context,
        user: typing.Optional[discord.Member],
    ):
        user = ctx.author if not user else user
        embed = self.bot.embed()
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        embed.set_thumbnail(url=str(user.avatar_url))
        embed.add_field(name="Roles", value=f"{len(user.roles)} roles")
        embed.add_field(
            name="Joined Server At",
            value=f"{user.joined_at.strftime('%A %b %Y %H:%M')}",
        )
        embed.add_field(
            name="Joined Discord At",
            value=f"{user.created_at.strftime('%A %b %Y %H:%M')}",
        )

        embed.add_field(
            name="Permissions",
            value=", ".join(
                map(
                    lambda b: b.replace("_", " ").capitalize(),
                    filter(
                        lambda a: True
                        if not a in ["__", "DEFAULT_VALUE", "VALID_FLAGS", "none"] and not a.startswith(("_", "all", "is"))
                        else False,
                        dir(user.guild_permissions),
                    ),
                )
            ),
        )
        await ctx.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Miscellaneous(bot))
