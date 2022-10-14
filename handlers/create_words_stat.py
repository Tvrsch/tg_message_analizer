import logging
import os
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from aiogram.handlers import MessageHandler
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy import text, select, distinct
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import UserFilter
from models import WordsStat

load_dotenv()

router = Router()

date_regexp = r"^([0-2][0-9]|(3)[0-1])(\.)(((0)[0-9])|((1)[0-2]))(\.)\d{4}$"


class GetStat(StatesGroup):
    select_chat = State()
    select_start_date = State()
    select_end_date = State()


@router.message(
    Command(commands=["stat"]),
    UserFilter(allowed_users=os.environ.get("ALLOWED_USERS", "").split(",")),
)
class GetChatHandler(MessageHandler):
    async def handle(self):
        state = self.data["state"]
        session = self.data["session"]
        chat_ids = (await session.scalars(select(distinct(WordsStat.chat_id)))).all()
        builder = ReplyKeyboardBuilder()
        for i in range(0, len(chat_ids)):
            builder.add(types.KeyboardButton(text=str(chat_ids[i])))
        builder.adjust(2)
        await self.event.answer(
            "Выберите чат по которому нужно сделать статистику:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
        await state.set_state(GetStat.select_chat)


@router.message(
    GetStat.select_chat,
)
async def chat_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chat=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите дату начала в формате: дд.мм.гггг",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(GetStat.select_start_date)


@router.message(
    GetStat.select_start_date,
    F.text.regexp(date_regexp),
)
async def start_date_chosen(message: types.Message, state: FSMContext):
    await state.update_data(start_date=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите дату окончания в формате: дд.мм.гггг",
    )
    await state.set_state(GetStat.select_end_date)


@router.message(
    GetStat.select_end_date,
    F.text.regexp(date_regexp),
)
class StatHandler(MessageHandler):
    async def _get_users_stats(self, session: AsyncSession, start_date: datetime, end_date: datetime, chat: int):
        stats = await session.execute(
            text(
                f"""select tg_user.tg_username, sum(words_number) as words from words_stat 
                join tg_user on tg_user.id = user_id 
                where tg_user.is_ignored is false and words_stat.created_at > '{start_date}'::date 
                and words_stat.created_at < '{end_date}'::date
                and words_stat.chat_id = {chat}
                group by tg_username;"""
            )
        )
        return stats

    async def _get_answer(self, start_date, end_date, chat) -> str:
        stats = await self._get_users_stats(self.data["session"], start_date, end_date, chat)
        sentence_list = [
            f"Пользователь {row['tg_username']} использовал {row['words']} слов."
            for row in stats
        ]
        answer_message = "\n".join(sentence_list)
        return answer_message

    async def handle(self):
        state = self.data["state"]
        user_data = await state.get_data()

        start_date = datetime.strptime(user_data["start_date"], "%d.%m.%Y")
        end_date = datetime.strptime(self.event.text.lower(), "%d.%m.%Y").replace(
            hour=23, minute=59
        )
        answer_message = await self._get_answer(start_date, end_date, int(user_data["chat"]))

        await self.event.answer(
            text=f"Дата начала: {start_date}\nДата окончания: {end_date}\nСтатистика:\n{answer_message}"
        )
        # Сброс состояния и сохранённых данных у пользователя
        await state.clear()


@router.message(GetStat.select_start_date)
async def start_date_chosen_incorrectly(message: types.Message):
    await message.answer(
        text="Некорректная дата, формат: дд.мм.гггг.",
    )


@router.message(GetStat.select_end_date)
async def end_date_chosen_incorrectly(message: types.Message):
    await message.answer(
        text="Некорректная дата, формат: дд.мм.гггг.",
    )
