import discord
from discord.ext import commands


class GuildManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

def setup(bot):
    bot.add_cog(GuildManagement(bot))
