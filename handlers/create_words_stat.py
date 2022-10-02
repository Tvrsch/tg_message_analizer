import os
from datetime import datetime
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from aiogram.handlers import MessageHandler
from sqlalchemy import text
from dotenv import load_dotenv

from filters.chat_types import UserFilter
from keyboards import make_row_keyboard

load_dotenv()

router = Router()

date_regexp = r"^([0-2][0-9]|(3)[0-1])(\.)(((0)[0-9])|((1)[0-2]))(\.)\d{4}$"


class GetStat(StatesGroup):
    select_start_date = State()
    select_end_date = State()


async def get_users_stats(session, start_date, end_date):
    stats = await session.execute(
        text(
            f"select tg_user.tg_username, sum(words_number) as words from words_stat join tg_user on tg_user.id = user_id where words_stat.created_at > '{start_date}'::date and words_stat.created_at < '{end_date}'::date group by tg_username;"
        )
    )
    return stats


@router.message(
    Command(commands=["stat"]),
    UserFilter(allowed_users=os.environ.get("ALLOWED_USERS", "").split(",")),
)
async def cmd_stat(message: types.Message, state: FSMContext):
    await message.answer(
        text="Напишите дату начала в формате: дд.мм.гггг",
    )
    await state.set_state(GetStat.select_start_date)


@router.message(
    GetStat.select_start_date,
    F.text.regexp(date_regexp),
)
async def start_date_chosen(message: types.Message, state: FSMContext):
    await state.update_data(start_date=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите дату окончания в формате: дд.мм.гггг"
    )
    await state.set_state(GetStat.select_end_date)


@router.message(
    GetStat.select_end_date,
    F.text.regexp(date_regexp),
)
class StatHandler(MessageHandler):
    async def handle(self):
        state = self.data["state"]
        user_data = await state.get_data()

        start_date = datetime.strptime(user_data["start_date"], "%d.%m.%Y")
        end_date = datetime.strptime(self.event.text.lower(), "%d.%m.%Y").replace(
            hour=23, minute=59
        )

        stats = await get_users_stats(self.data["session"], start_date, end_date)
        sentence_list = [
            f"Пользователь {row['tg_username']} использовал {row['words']} слов."
            for row in stats
        ]
        answer_message = "\n".join(sentence_list)
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
