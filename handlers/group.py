from aiogram import types, Router
from aiogram.handlers import MessageHandler
from sqlalchemy import select

from filters.chat_types import ChatTypeFilter, LanguageTypeFilter
from models import WordsStat, TgUser

router = Router()


@router.message(
    ChatTypeFilter(chat_type=["group", "supergroup"]),
    LanguageTypeFilter(language_type="en"),
    content_types="text",
)
class GroupHandler(MessageHandler):
    async def handle(self):
        tg_user_id = self.event.from_user.id
        words = self.event.text.split()
        refined_words = [w for w in words if not w.isdigit() and len(w) >= 2]
        if len(refined_words) < 3:
            return

        session = self.data["session"]

        bd_user = (
            await session.execute(select(TgUser).where(TgUser.tg_id == tg_user_id))
        ).scalar()

        if not bd_user:
            bd_user = TgUser(
                tg_username=self.event.from_user.username, tg_id=tg_user_id
            )
            session.add(bd_user)
            await session.commit()
            bd_user = (
                await session.execute(select(TgUser).where(TgUser.tg_id == tg_user_id))
            ).scalar()
        session.add(
            WordsStat(
                user_id=bd_user.id,
                chat_id=self.event.chat.id,
                words_number=len(refined_words),
                sentence=self.event.text,
            )
        )
        await session.commit()
