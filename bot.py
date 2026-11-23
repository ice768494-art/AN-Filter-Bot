# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

# Clone Code Credit : YT - @Tech_VJ / TG - @VJ_Bots / GitHub - @VJBots

import importlib, logging, logging.config, pytz, asyncio
from pathlib import Path
from pyrogram.handlers.handler import Handler

# Create the bot event loop before importing modules that create Motor clients.
# Motor must use the same loop that runs start().
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

from pyrogram import Client, idle
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from Script import script 
from datetime import date, datetime 
from aiohttp import web
from plugins import web_server
from plugins.clone import restart_bots

from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

def load_plugins():
    """Import every plugin module and collect its Pyrogram handlers.

    Plugins use the class-level decorators (@Client.on_message, ...). Those only
    tag the function with a `.handlers` list; they do NOT register anything on
    their own. Pyrogram registers them only when the client is created with
    `plugins={"root": ...}`. Because plugins are imported manually here, we must
    collect and register the handlers ourselves, otherwise the bot connects but
    never answers any message.
    """
    collected = []
    seen = set()
    for plugin_path in sorted(Path("plugins").rglob("*.py")):
        if plugin_path.name == "__init__.py":
            continue
        relative = plugin_path.relative_to(Path("plugins")).with_suffix("")
        module_name = "plugins." + ".".join(relative.parts)
        module = importlib.import_module(module_name)
        for obj in list(vars(module).values()):
            if not callable(obj):
                continue
            func_handlers = getattr(obj, "handlers", None)
            if not isinstance(func_handlers, list):
                continue
            for item in func_handlers:
                try:
                    handler, group = item
                except (TypeError, ValueError):
                    continue
                if isinstance(handler, Handler) and isinstance(group, int) and id(handler) not in seen:
                    seen.add(id(handler))
                    collected.append((handler, group))
        logging.info("Loaded plugin: %s", module_name)
    return collected


def register_handlers(handlers):
    for handler, group in handlers:
        TechVJBot.add_handler(handler, group)
    logging.info("Registered %d handlers", len(handlers))
    if not handlers:
        logging.error("NO HANDLERS REGISTERED - the bot will not respond to anything!")


async def start_web_server():
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", PORT).start()
    logging.info("Web server listening on 0.0.0.0:%s", PORT)


async def start():
    print('\n')
    print('Initializing Your Bot')
    plugin_handlers = load_plugins()
    # Open the HTTP port immediately so Render's port scan / health check passes.
    await start_web_server()
    await TechVJBot.start()
    register_handlers(plugin_handlers)
    await asyncio.sleep(0)  # let the dispatcher apply the queued add_handler tasks
    await initialize_clients()
    if ON_HEROKU or ON_RENDER:
        asyncio.create_task(ping_server())
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    try:
        await TechVJBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    except:
        print("Make Your Bot Admin In Log Channel With Full Rights")
    for ch in CHANNELS:
        try:
            k = await TechVJBot.send_message(chat_id=ch, text="**Bot Restarted**")
            await k.delete()
        except:
            print("Make Your Bot Admin In File Channels With Full Rights")
    try:
        k = await TechVJBot.send_message(chat_id=AUTH_CHANNEL, text="**Bot Restarted**")
        await k.delete()
    except:
        print("Make Your Bot Admin In Force Subscribe Channel With Full Rights")
    if CLONE_MODE == True:
        print("Restarting All Clone Bots.......")
        try:
            await restart_bots()
            print("Restarted All Clone Bots.")
        except Exception:
            logging.exception("Failed restarting clone bots")
    logging.info("Bot is up and listening for updates")
    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
    finally:
        loop.close()


