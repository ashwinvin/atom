import asyncio
import logging

import asyncpg
import discord

from atom.bot import Atom, loadall
from atom.help import AtomHelp
from config import BotConfig, bot_intents

config = BotConfig()
db = asyncio.get_event_loop().run_until_complete(asyncpg.create_pool(dsn=config.PGDSN))
logger = logging.getLogger(__name__)

bot = Atom(
    command_prefix=config.PREFIX,
    owner_id=534615931603779617,
    intents=bot_intents(),
    db=db,
    error_channel=config.CError,
    config=config,
)
bot.help_command = AtomHelp()

loadall(bot)


@bot.event
async def on_ready():
    # logger.info(f"Invite me using {discord.utils.oauth_url(bot.user.id)}")
    logger.info(f"Bot is and ready to use! I can see {len(bot.guilds)} guilds.")


bot.run(config.TOKEN)
