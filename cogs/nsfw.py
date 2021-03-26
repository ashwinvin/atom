from discord.ext import commands

class Nsfw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def cog_check(self, ctx: commands.Context):
        if ctx.channel.is_nsfw():
           return True
        return False

    async def 

def setup(bot):
    bot.add_cog(Nsfw(bot))