import logging
import os

from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from middleware import DbMiddleware
from handlers import group, common, create_words_stat

from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)

load_dotenv()


async def on_startup(bot: Bot, base_url: str):
    await bot.set_webhook(f"{base_url}/webhook")


def main():
    bot = Bot(token=os.environ["BOT_TOKEN"])

    dp = Dispatcher(storage=MemoryStorage())
    dp["base_url"] = os.environ["APP_BASE_URL"]
    dp.startup.register(on_startup)

    dp.include_router(group.router)
    dp.include_router(common.router)
    dp.include_router(create_words_stat.router)

    group.router.message.middleware(DbMiddleware())
    group.router.edited_message.middleware(DbMiddleware())
    create_words_stat.router.message.middleware(DbMiddleware())
    common.router.message.middleware(DbMiddleware())

    app = Application()
    app["bot"] = bot

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    run_app(app, host="localhost", port=8001)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
