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
