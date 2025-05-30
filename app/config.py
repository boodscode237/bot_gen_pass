import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PASSWORDS_FILE = "passwords.json"
DEFAULT_PASSWORD_LENGTH = 16
