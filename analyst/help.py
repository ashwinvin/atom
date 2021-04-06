import discord
from discord.ext import commands

class AnalystHelp(commands.HelpCommand):

    def get_command_signature(self, command):
        return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        hembed = self.context.bot.embed(title="Help") 
        hembed.set_footer(text="Made By Shahad!!")
        for cog, commands in mapping.items():
            command_signatures = [self.get_command_signature(c) for c in commands if not c.hidden]
            if command_signatures:  
                cog_name = getattr(cog, "qualified_name", "No Category")
                if cog_name == "Jishaku" or cog_name =="DevTools":
                    continue
                hembed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        channel = self.get_destination()
        await channel.send(embed=hembed)
    
    async def send_command_help(self, command):
        embed = self.context.bot.embed(title=self.get_command_signature(command))
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
