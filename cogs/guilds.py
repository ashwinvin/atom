import discord
import typing
import asyncio
from discord.ext import commands


class GuildManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afkers = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id in self.afkers.keys():
            self.afkers.pop(message.author.id)
            await message.channel.send(embed=self.bot.embed(description=f"Welcome back {message.author.mention}", colorful=False))
            try:
                await message.author.edit(nick=message.author.display_name[5:])
            except discord.Forbidden:
                await message.channel.send("Failed to change your nickname!! Permissions Denied!!", delete_after=10)
        if n := discord.utils.find(lambda n: n.id in self.afkers.keys(), message.mentions):
            await message.reply(embed=self.bot.embed(description=f"Sorry but `{n.display_name}` is afk \n Reason:```{self.afkers[n.id]}```"))

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def poll(self, ctx, description: str, choice1: str, choice2: str ):
        """"""
        description = f"{description} \n \n \U0001f170 {choice1} \n \U0001f171 {choice2}" 
        poll_embed = self.bot.embed(
            title="Poll", color=0x77fc03, description="".join(description), colorful=False
        )
        poll_embed.set_footer(text=f"Poll started by {ctx.author.name}")
        msg = await ctx.send(embed=poll_embed)
        await msg.add_reaction("\U0001f170")
        await msg.add_reaction("\U0001f171")

    @commands.command()
    async def afk(self, ctx, *reason: typing.Optional[str]):
        if not reason:
            reason = "Unknown"
        await ctx.send(embed=self.bot.embed(description=f"I have set your afk status to `{''.join(reason)}`", colorful=False))
        try:
            await ctx.author.edit(nick=f"[AFK]{ctx.author.display_name}")
        except discord.Forbidden:
            await ctx.send("Failed to change your nickname!! Permissions Denied!!", delete_after=10)
        await asyncio.sleep(2)
        self.afkers[ctx.author.id] = "".join(reason)

    @commands.command()
    async def bots(self, ctx):
        description = ""
        for member in ctx.guild.members:
            if member.bot:
                description += f"{member.mention} joined at {str(member.joined_at.strftime('%Y:%m:%d'))} \n" 
                pass
            
        embed = self.bot.embed(title=f"Bots in {ctx.guild.name}", description=description)
        await ctx.send(embed=embed)
        
    @commands.command()
    async def info(
        self,
        ctx: commands.Context,
        inquiry: typing.Optional[typing.Union[discord.Member, discord.Role]],
    ):
        if not inquiry:
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
                name="Emojis", value=f"Total {len(ctx.guild.emojis)} emojis"
            )
            embed.add_field(name="Roles", value=len(ctx.guild.roles))
            embed.set_thumbnail(url=ctx.guild.icon_url)
            await ctx.send(embed=embed)
        if type(inquiry) == discord.Member:
            embed = self.bot.embed()
            embed.set_author(name=inquiry.display_name, icon_url=inquiry.avatar_url)
            
            pass


def setup(bot):
    bot.add_cog(GuildManagement(bot))
