from aiogram.enums import ChatType
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from config import settings


class AdminFilter(Filter):
    async def __call__(self, obj: Message | CallbackQuery) -> bool:
        if isinstance(obj, CallbackQuery):
            # Если это CallbackQuery, получаем chat из message
            if not obj.message or not obj.message.chat:
                return False
            chat_type = obj.message.chat.type
            user_id = obj.from_user.id
        else:
            # Если это Message, получаем chat напрямую
            chat_type = obj.chat.type
            user_id = obj.from_user.id

        # Проверяем тип чата
        if chat_type != ChatType.PRIVATE:
            return False

        # Отладочный вывод
        is_admin = settings.ADMINS and str(user_id) in settings.ADMINS
        # print(f"Admin check: User ID {user_id}, Admin IDs: {settings.ADMINS}, Is admin: {is_admin}")

        # Проверяем ID пользователя
        return is_admin
