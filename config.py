from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()


@dataclass
class BotConfig:
    TOKEN = os.getenv("TOKEN")
    PGDSN = os.getenv("POSTGRESURI")
    PREFIX = os.getenv("PREFIX")
