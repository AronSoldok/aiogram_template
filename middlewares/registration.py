from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from keyboards.user.registration import timezone_kb
from supportiv_function.base import SupportiveFunctions
from services.activity_service import get_or_create_user, get_or_create_user_stats


class RegistrationRequiredMiddleware(BaseMiddleware):
	async def __call__(self, handler, event, data):
		# Разрешаем сам процесс регистрации
		if isinstance(event, Message):
			text = (event.text or "").strip()
			if text.startswith("/register"):
				return await handler(event, data)
		elif isinstance(event, CallbackQuery):
			if event.data and event.data.startswith("reg:"):
				return await handler(event, data)

		# Гарантируем наличие пользователя и статистики
		user_id = event.from_user.id if hasattr(event, "from_user") else None
		if not user_id:
			return await handler(event, data)
		user = await get_or_create_user(user_id, getattr(event.from_user, "username", None), getattr(event.from_user, "full_name", None))
		stats = await get_or_create_user_stats(user.id)
		if not stats.is_registered:
			prompt = (
				"Пожалуйста, пройдите быструю регистрацию перед использованием.\n"
				"Выберите ваш часовой пояс:"
			)
			# Сообщение или редактирование
			if isinstance(event, CallbackQuery):
				await SupportiveFunctions.try_edit(event, text=prompt, reply_markup=timezone_kb())
				await event.answer()
			else:
				await event.answer(prompt, reply_markup=timezone_kb())
			return None

		return await handler(event, data) 