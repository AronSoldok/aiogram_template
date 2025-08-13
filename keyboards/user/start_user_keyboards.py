from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Сегодня", callback_data="menu:mark_today")],
        [InlineKeyboardButton(text="Отметить сегодняшний день", callback_data="menu:calendar:today")],
        [InlineKeyboardButton(text="Посмотреть статистику", callback_data="menu:stats:month")],
        [InlineKeyboardButton(text="🏆 Топ 10", callback_data="menu:top")],
    ])
