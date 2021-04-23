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

# Gino has an obnoxiously loud log for all queries executed, not great when inserting
# tens of thousands of users, so we can disable that (it's just a SQLAlchemy logger)
logging.getLogger("gino.engine._SAEngine").setLevel(logging.WARNING)
