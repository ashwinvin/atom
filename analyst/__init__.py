import os

import logging

import coloredlogs


__version__ = "1.1.1"

# Set root log level
logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s: %(message)s", level=logging.INFO)
coloredlogs.install(level=logging.INFO)

# Set Discord.py log level
logging.getLogger("discord.client").setLevel(logging.INFO)
logging.getLogger("asyncio").setLevel(logging.DEBUG)
