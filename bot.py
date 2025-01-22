import logging
import logging.config
import time
from pyrogram import Client, __version__
from pyrogram.raw.all import layer

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR
from utils import temp

class Bot(Client):
    def __init__(self):
        # Initialize the bot with necessary parameters
        super().__init__(
            session_name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        # Ensure system time is synchronized
        time.time()  # Sync system time before starting the bot

        # Fetch banned users and chats from the database
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        
        # Start the bot with proper initialization
        await super().start()

        # Ensure necessary indexes are created for the Media collection
        await Media.ensure_indexes()

        # Fetch bot's details and set global variables
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username

        # Log bot's start information
        logging.info(f"{me.first_name} (Pyrogram v{__version__}, Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)

    async def stop(self, *args):
        # Stop the bot and log the shutdown
        await super().stop()
        logging.info("Bot stopping and restarting process initiated.")

# Create an instance of the Bot class and run it
app = Bot()
app.run()
