import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from middleware import DbMiddleware
from handlers import group, common, create_words_stat

load_dotenv()


# Запуск процесса поллинга новых апдейтов
async def main():
    # Объект бота
    bot = Bot(token=os.environ["BOT_TOKEN"])
    # Диспетчер
    dp = Dispatcher(storage=MemoryStorage())
    group.router.message.middleware(DbMiddleware())
    create_words_stat.router.message.middleware(DbMiddleware())
    dp.include_router(group.router)
    dp.include_router(common.router)
    dp.include_router(create_words_stat.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())