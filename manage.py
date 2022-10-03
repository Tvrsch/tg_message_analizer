import asyncio
import logging
import os

from aiohttp.web import run_app
from aiohttp.web_app import Application
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from middleware import DbMiddleware
from handlers import group, common, create_words_stat

from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,
)

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

load_dotenv()

APP_BASE_URL = "http://127.0.0.1:8081"


async def on_startup(bot: Bot, base_url: str):
    await bot.set_webhook(f"{base_url}/webhook")



def main():
    bot = Bot(token=os.environ["BOT_TOKEN"])

    dp = Dispatcher(storage=MemoryStorage())
    dp["base_url"] = APP_BASE_URL
    dp.startup.register(on_startup)

    dp.include_router(group.router)
    dp.include_router(common.router)
    dp.include_router(create_words_stat.router)

    group.router.message.middleware(DbMiddleware())
    create_words_stat.router.message.middleware(DbMiddleware())

    app = Application()
    app["bot"] = bot

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    run_app(app, host="127.0.0.1", port=8081)


if __name__ == "__main__":
    main()
