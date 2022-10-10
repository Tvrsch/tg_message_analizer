import os

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from aiogram.types import Message
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
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
