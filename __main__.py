import logging
import discord
import asyncpg
from analyst.help import AnalystHelp
import asyncio
from analyst.bot import Analyst, loadall

from config import BotConfig

config = BotConfig()
db = asyncio.get_event_loop().run_until_complete(asyncpg.create_pool(dsn=config.PGDSN))
logger = logging.getLogger(__name__)

bot = Analyst(command_prefix="a!", intents=discord.Intents.all(), db=db, error_channel=config.CError)
bot.help_command = AnalystHelp()

loadall(bot)


@bot.event
async def on_ready():
    logger.info(f"Invite me using {discord.utils.oauth_url(bot.user.id)}")
    logger.info(f"Bot is and ready to use! I can see {len(bot.guilds)} guilds.")


bot.run(config.TOKEN)
