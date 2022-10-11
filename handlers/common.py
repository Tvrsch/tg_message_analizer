import os

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.handlers import MessageHandler
from aiogram.types import Message
from sqlalchemy import update, select

from filters.chat_types import UserFilter
from models import TgUser

router = Router()


@router.message(
    Command(commands=["users"]),
    UserFilter(allowed_users=os.environ.get("ALLOWED_USERS", "").split(",")),
)
class GetUsers(MessageHandler):
    async def handle(self):
        session = self.data["session"]
        users = await session.execute(select(TgUser.tg_id, TgUser.tg_username))
        sentence_list = [
            f"Пользователь {row['tg_username']} id {row['tg_id']} В игноре? {row['is_ignored']}"
            for row in users
        ]
        answer_message = "\n".join(sentence_list)

        await self.event.answer(text=f"{answer_message}")


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="""Запросить статистику сообщений пользователей можно с помощью команды /stat\n
        Узнать какие пользователи есть можно с помощью команды /users\n
        Добавить пользователя в игнор лист статистики можно с помощью команды /add_ignore\n
        Убрать пользователя из игнор листа статистики можно с помощью команды /remove_ignore""",
    )


@router.message(
    Command(commands=["add_ignore"]),
    UserFilter(allowed_users=os.environ.get("ALLOWED_USERS", "").split(",")),
)
class AddUserIgnore(MessageHandler):
    async def handle(self):
        session = self.data["session"]
        ignore_user = int(self.event.text.lower())
        await session.execute(update(TgUser).where(TgUser.tg_id == ignore_user).values(is_ignore=True))
        await self.event.answer(text=f"Пользователь {ignore_user} добавлен в игнор лист")

@router.message(
    Command(commands=["remove_ignore"]),
    UserFilter(allowed_users=os.environ.get("ALLOWED_USERS", "").split(",")),
)
class RemoveUserIgnore(MessageHandler):
    async def handle(self):
        session = self.data["session"]
        unignore_user = int(self.event.text.lower())
        await session.execute(update(TgUser).where(TgUser.tg_id == unignore_user).values(is_ignore=False))
        await self.event.answer(text=f"Пользователь {unignore_user} убран из игнор листа")


@router.message(Command(commands=["cancel"]))
@router.message(Text(text="отмена", text_ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Действие отменено")
