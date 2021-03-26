import discord
import typing
from discord.ext import commands


class GManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def poll(self, ctx, *description: str):
        poll_embed = discord.Embed(
            title="Poll", color=0x008000, description=description
        )
        msg: discord.Message = await ctx.send(embed=poll_embed)
        await msg.add_reaction("⬆️")
        await msg.add_reaction("⬇️")

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
