from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os


load_dotenv()

# Set root path
BASE_DIR = Path(__file__).resolve().parent.parent

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_URL = os.getenv('DB_URL')


@dataclass
class MongoConfig:
    url: str
    db: str
    collection: str


# Config MongoDB
mongo_config = MongoConfig(
    os.getenv('DB_URL'),
    os.getenv('DB_NAME'),
    os.getenv('DB_COLLECTION')
)

