from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message
from langdetect import detect, LangDetectException


class ChatTypeFilter(BaseFilter):
    chat_type: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class LanguageTypeFilter(BaseFilter):
    language_type: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        try:
            if isinstance(self.language_type, str):
                return detect(message.text) == self.language_type
            else:
                return detect(message.text) in self.language_type
        except LangDetectException:
            return False


class UserFilter(BaseFilter):
    allowed_users: Union[str, list]

    async def __call__(self, message: Message) -> bool:
        if isinstance(self.allowed_users, str):
            return str(message.from_user.id) == self.allowed_users
        else:
            return str(message.from_user.id) in self.allowed_users
