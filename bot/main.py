import os
import logging
from prometheus_client import start_http_server
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
)

import database
from handlers import send_menu_to_channel, button_callback_handler, start_handler
from metrics import TRACKS_SENT


logging.basicConfig(level=logging.INFO)


def load_config():
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError("BOT_TOKEN not set")
    return bot_token


async def on_startup(app):
    database.init_databases()
    await send_menu_to_channel(app)


def main():
    token = load_config()
    # expose metrics for Prometheus
    start_http_server(8000)

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CallbackQueryHandler(button_callback_handler))
    application.add_handler(CommandHandler("start", start_handler))

    application.run_polling(after_startup=on_startup)


if __name__ == "__main__":
    main()
