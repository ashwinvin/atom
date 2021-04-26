import discord
from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()


@dataclass
class BotConfig:
    TOKEN = os.getenv("TOKEN")
    PGDSN = os.getenv("POSTGRESURI")
    PREFIX = os.getenv("PREFIX")
    DevGuild = os.getenv("Dev_Guild")
    CError = os.getenv("Error_Channel")
    LAVALINK_IP = os.getenv("LAVALINK_IP")
    LAVALINK_PORT = os.getenv("LAVALINK_PORT")
    LAVALINK_PASS = os.getenv("LAVALINK_PASS")
    REDIS_IP = os.getenv("REDIS_IP")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_NAMESPACE = os.getenv("REDIS_NAMESPACE")
    REDIS_DB = os.getenv("REDIS_DB")


def bot_intents() -> discord.Intents:
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    intents.bans = True
    intents.emojis = True
    intents.integrations = False
    intents.webhooks = False
    intents.invites = False
    intents.voice_states = True
    intents.presences = True
    intents.messages = True
    intents.reactions = True
    intents.typing = False
    return intents
