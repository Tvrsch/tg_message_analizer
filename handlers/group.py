from aiogram import types, Router
from aiogram.handlers import MessageHandler
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter, LanguageTypeFilter
from models import WordsStat, TgUser

router = Router()


async def get_or_create_user(session: AsyncSession, tg_user_id: int, tg_username) -> TgUser:
    bd_user = (
        await session.execute(select(TgUser).where(TgUser.tg_id == tg_user_id))
    ).scalar()

    if not bd_user:
        bd_user = TgUser(
            tg_username=tg_username, tg_id=tg_user_id
        )
        session.add(bd_user)
        await session.commit()
        bd_user = (
            await session.execute(select(TgUser).where(TgUser.tg_id == tg_user_id))
        ).scalar()
    return bd_user


def count_words(text: str) -> [list, int]:
    words = text.split()
    refined_words = [w for w in words if not w.isdigit() and len(w) >= 2]
    return refined_words, len(refined_words)

@router.message(
    ChatTypeFilter(chat_type=["group", "supergroup"]),
    LanguageTypeFilter(language_type="en"),
    content_types="text",
)
class GroupHandler(MessageHandler):
    async def handle(self):
        words, words_count = count_words(self.event.text)
        if words_count < 3:
            return

        session = self.data["session"]
        bd_user = await get_or_create_user(session, self.event.from_user.id, self.event.from_user.username)
        session.add(
            WordsStat(
                user_id=bd_user.id,
                chat_id=self.event.chat.id,
                message_id=self.event.message_id,
                words_number=words_count,
                sentence=self.event.text,
            )
        )
        await session.commit()


@router.message(
    ChatTypeFilter(chat_type=["group", "supergroup"]),
    LanguageTypeFilter(language_type="en"),
    content_types="text",
)
class EditedGroupHandler(MessageHandler):
    async def handle(self):
        session = self.data["session"]
        message = await session.execute(select(WordsStat).where(WordsStat.message_id == self.event.message_id))
        if message:
            words, words_count = count_words(self.event.text)
            if words_count < 3:
                return
            await session.execute(
                update(WordsStat).where(
                    WordsStat.message_id == self.event.message_id
                ).values(
                    words_number=words_count, sentence=self.event.text
                )
            )
            await session.commit()
