import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PASSWORDS_FILE = "passwords.json"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

DEFAULT_PASSWORD_LENGTH = 16
