from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from keyboards.user.registration import timezone_kb, reminder_time_kb
from supportiv_function.base import SupportiveFunctions
from database.models.user import User
from database.models.user_stats import UserStats


registration_router = Router(name="registration")


@registration_router.message(Command("register"))
async def start_registration(msg: Message):
    await msg.answer("Выберите ваш часовой пояс:", reply_markup=timezone_kb())


@registration_router.callback_query(F.data.startswith("reg:tz:"))
async def choose_timezone(cb: CallbackQuery):
    tz = cb.data.split(":", 2)[2]
    user = await User.get(tg_id=cb.from_user.id)
    user.timezone = tz
    await user.save()
    await SupportiveFunctions.try_edit(cb, text="Выберите время напоминаний:", reply_markup=reminder_time_kb())
    await cb.answer()


@registration_router.callback_query(F.data.startswith("reg:rem:"))
async def choose_reminder(cb: CallbackQuery):
    _, _, value = cb.data.split(":", 2)
    stats, _ = await UserStats.get_or_create(user_id=(await User.get(tg_id=cb.from_user.id)).id)
    if value == "none":
        stats.reminder_time = None
    else:
        stats.reminder_time = value
    stats.is_registered = True
    await stats.save()
    await SupportiveFunctions.try_edit(cb, text="Регистрация завершена!", reply_markup=None)
    await cb.answer("Сохранено") 