import discord
import asyncio
from discord.ext import commands


class announcements(commands.Cog, name="Announcements"):
    """
    Announcements Help
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, help="Used For Announcing ")
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx):
        def checkM(message: discord.Message):
            return message.channel == ctx.channel and message.author == ctx.author

        def checkR(message: discord.Message):
            return (
                message.channel == ctx.channel
                and message.author == ctx.author
                and message.content != "None"
            )

        def checkC(message: discord.Message):
            return (
                message.channel == ctx.channel
                and message.author == ctx.author
                and len(message.channel_mentions) != 0
            )

        await ctx.send("Alright, what do you want to announce?")
        description = await self.bot.wait_for("message", check=checkM)
        description = description.content

        await ctx.send("Give me a title for the announcement")
        title = await self.bot.wait_for("message", check=checkM)
        title = title.content

        await ctx.send("Where should I post The announcement")
        channel = await self.bot.wait_for("message", check=checkC)

        await ctx.send("Whom should I ping (ping the role or Give None)")
        role = await self.bot.wait_for("message", check=checkR)

        embed = self.bot.embed(title=title, description=description, color=0x47E022)
        embed.set_footer(
            text=f"{ctx.guild.name}   - Announced by {ctx.message.author.display_name}"
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/616315208251605005/616319462349602816/Tw.gif"
        )
        try:
            channel_id = channel.channel_mentions[0].id
            channel = self.bot.get_channel(channel_id)
            disappear = await channel.send(f"{role.content}")
            await channel.send(embed=embed)
            await asyncio.sleep(1)
            await disappear.delete()
        except Exception as e:
            print(e)
            await ctx.send("Failed to send the **_Announcement_**")
            await ctx.send("Try changing the channel or infrom the Devloper")


def setup(bot):
    bot.add_cog(announcements(bot))
