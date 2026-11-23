
# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

# Clone Code Credit : YT - @Tech_VJ / TG - @VJ_Bots / GitHub - @VJBots

import importlib
import logging
import logging.config
import pytz
import asyncio

from pathlib import Path
from datetime import date, datetime
from typing import Union, Optional, AsyncGenerator

from aiohttp import web
from pyrogram import Client, idle

# Create ONE event loop before importing database modules.
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Logging configuration
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

# Bot imports
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server
from plugins.clone import restart_bots

from TechVJ.bot import TechVJBot
from TechVJ.bot.clients import initialize_clients, multi_clients
from TechVJ.util.keepalive import ping_server


def load_plugins():
    """Import plugin modules once, including nested plugin folders."""
    for plugin_path in sorted(Path("plugins").rglob("*.py")):
        if plugin_path.name == "__init__.py":
            continue

        relative = plugin_path.relative_to(
            Path("plugins")
        ).with_suffix("")

        module_name = "plugins." + ".".join(relative.parts)

        importlib.import_module(module_name)
        logging.info("Loaded plugin: %s", module_name)


async def stop_clients():
    """Stop all connected Pyrogram clients gracefully."""

    clients = list(multi_clients.values())

    if TechVJBot not in clients:
        clients.append(TechVJBot)

    for client in reversed(clients):
        try:
            if client and client.is_connected:
                await client.stop()
                logging.info("Pyrogram client stopped")

        except Exception:
            logging.exception("Error stopping Pyrogram client")


async def start():
    app = None
    keepalive_task = None

    try:
        print("\n")
        print("Initializing Your Bot")

        # Load plugins
        load_plugins()

        # Start main bot
        await TechVJBot.start()

        # Initialize additional clients
        await initialize_clients()

        # Keepalive
        if ON_HEROKU:
            keepalive_task = asyncio.create_task(ping_server())

        # Database
        b_users, b_chats = await db.get_banned()

        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        # Bot information
        me = await TechVJBot.get_me()

        temp.BOT = TechVJBot
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name

        logging.info(script.LOGO)

        # Time information
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")

        # Restart message
        try:
            await TechVJBot.send_message(
                chat_id=LOG_CHANNEL,
                text=script.RESTART_TXT.format(today, time)
            )
        except Exception:
            logging.exception(
                "Make Your Bot Admin In Log Channel With Full Rights"
            )

        # File channels
        for ch in CHANNELS:
            try:
                msg = await TechVJBot.send_message(
                    chat_id=ch,
                    text="**Bot Restarted**"
                )
                await msg.delete()

            except Exception:
                logging.exception(
                    "Make Your Bot Admin In File Channels With Full Rights"
                )

        # Force subscription channel
        try:
            msg = await TechVJBot.send_message(
                chat_id=AUTH_CHANNEL,
                text="**Bot Restarted**"
            )
            await msg.delete()

        except Exception:
            logging.exception(
                "Make Your Bot Admin In Force Subscribe Channel With Full Rights"
            )

        # Restart clone bots
        if CLONE_MODE:
            print("Restarting All Clone Bots.......")

            await restart_bots()

            print("Restarted All Clone Bots.")

        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()

        bind_address = "0.0.0.0"

        await web.TCPSite(
            app,
            bind_address,
            PORT
        ).start()

        logging.info("Web server started on port %s", PORT)

        # Keep bot alive
        await idle()

    finally:
        logging.info("Starting graceful shutdown...")

        # Stop keepalive
        if keepalive_task:
            keepalive_task.cancel()

            await asyncio.gather(
                keepalive_task,
                return_exceptions=True
            )

        # Stop web server
        if app:
            try:
                await app.cleanup()
                logging.info("Web server stopped")

            except Exception:
                logging.exception("Web server cleanup failed")

        # Stop Pyrogram clients
        await stop_clients()

        logging.info("Shutdown completed")


if __name__ == '__main__':

    try:
        loop.run_until_complete(start())

    except KeyboardInterrupt:
        logging.info("Service Stopped Bye 👋")

    except Exception:
        logging.exception("Bot stopped because of an error")

    finally:
        try:
            pending = [
                task for task in asyncio.all_tasks(loop)
                if not task.done()
            ]

            for task in pending:
                task.cancel()

            if pending:
                loop.run_until_complete(
                    asyncio.gather(
                        *pending,
                        return_exceptions=True
                    )
                )

            loop.run_until_complete(
                loop.shutdown_asyncgens()
            )

        except Exception:
            logging.exception("Final event loop cleanup failed")

        finally:
            loop.close()
