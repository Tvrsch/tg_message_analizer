import os
from datetime import datetime
from asyncio import current_task
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)

load_dotenv()
engine = create_async_engine(os.environ["DB_CONNECTION"], echo=True)


class DbMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        print("Before handler")
        async_session = sessionmaker(bind=engine, class_=AsyncSession)
        async with async_session() as session:
            data["session"] = session
            result = await handler(event, data)

        print("After handler")
        return result
