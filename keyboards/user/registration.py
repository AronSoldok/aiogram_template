from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def timezone_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="UTC", callback_data="reg:tz:UTC")],
        [InlineKeyboardButton(text="Европа/Москва", callback_data="reg:tz:Europe/Moscow")],
        [InlineKeyboardButton(text="Европа/Киев", callback_data="reg:tz:Europe/Kyiv")],
        [InlineKeyboardButton(text="Азия/Алматы", callback_data="reg:tz:Asia/Almaty")],
    ])


def reminder_time_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="06:00", callback_data="reg:rem:06:00"), InlineKeyboardButton(text="08:00", callback_data="reg:rem:08:00"), InlineKeyboardButton(text="10:00", callback_data="reg:rem:10:00")],
        [InlineKeyboardButton(text="18:00", callback_data="reg:rem:18:00"), InlineKeyboardButton(text="20:00", callback_data="reg:rem:20:00"), InlineKeyboardButton(text="21:00", callback_data="reg:rem:21:00")],
        [InlineKeyboardButton(text="Без напоминаний", callback_data="reg:rem:none")],
    ]) 