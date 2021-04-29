import discord
from discord.ext import commands
from reactionmenu import ReactionMenu, Button, ButtonType


class AtomHelp(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.verify_checks = True
        self.show_hidden = False

    def get_command_signature(self, command):
        return "%s%s %s" % (
            self.clean_prefix,
            command.qualified_name,
            command.signature,
        )

    async def send_bot_help(self, mapping):
        bot = self.context.bot

        async def button_action(*args):
            for arg in args:
                print(type(arg))

        cmd_info = {
            "total": len(self.context.bot.commands),
            "available": len(await self.filter_commands(self.context.bot.commands)),
        }

        notice = f"```- [] = optional argument \n- <> = required argument \n- Do NOT type these when using commands!```  \
        Total Commands:{cmd_info['total']} | Usable by you: {cmd_info['available']}"

        Membed = discord.Embed(color=0xFFD105, description=notice)
        Membed.set_author(icon_url=self.context.author.avatar_url, name=self.context.author.name)

        menu = ReactionMenu(self.context, back_button="◀️", next_button="▶️", config=ReactionMenu.STATIC)

        for cog, _ in mapping.items():
            if hasattr(cog, "qualified_name"):
                if cog.qualified_name in ["Jishaku", "DevTools"]:
                    continue
                Membed.add_field(
                    name=cog.qualified_name,
                    value=cog.description if cog.description else "Documentation in Progress",
                )
                cog_embed = self.create_cog_help(cog)
                cog_emoji = discord.utils.get(bot.emojis, id=cog.emoji)
                cog_button = Button(
                    emoji=str(cog_emoji),
                    linked_to=ButtonType.CUSTOM_EMBED,
                    embed=cog_embed,
                )
                menu.add_button(cog_button)

        menu.add_page(Membed)
        await menu.start()

    def create_cog_help(self, cog):
        cog_embed = discord.Embed(color=0xFFD105, description=cog.description, title=cog.qualified_name)
        cog_embed.set_author(icon_url=self.context.author.avatar_url, name=self.context.author.name)
        for command in cog.get_commands():
            cog_embed.add_field(name=command.qualified_name, value=command.help or "Documentation In Progress")
        return cog_embed

    async def send_cog_help(self, cog):
        return await self.get_destination().send(embed=self.create_cog_help(cog))

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), color=0xFFD105)
        embed.add_field(name="Help", value=command.help or "Documentation In Progress")
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)
