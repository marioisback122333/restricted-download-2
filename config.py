import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

USER = os.environ.get("DB_USER")
PASS = os.environ.get("DB_PASS")
# ==============================
# Telegram Bot Credentials
# ==============================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")


# ==============================
# Admin Configuration
# ==============================

# Add admin user IDs separated by commas in environment variables
ADMINS = [int(admin) for admin in os.environ.get("ADMINS", "").split(",") if admin]


# ==============================
# Database Configuration
# ==============================

DB_URI = f"mongodb+srv://{quote_plus(USER)}:{quote_plus(PASS)}@cluster0.cpbr4cp.mongodb.net/?appName=Cluster0"
DB_NAME = os.environ.get("DB_NAME", "SaveRestricted2")


# ==============================
# Logging Configuration
# ==============================

# Replace with your Telegram log channel ID (example: -1001234567890)
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))


# ==============================
# Error Handling
# ==============================

# Set to True to send error messages to users
ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "True").lower() == "true"
