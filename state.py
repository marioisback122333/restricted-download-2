# Shared runtime state between bot.py and plugins
# This avoids the __main__ vs module import issue

BOT_LOCKED = False
