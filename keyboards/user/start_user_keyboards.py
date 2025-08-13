from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отметить сегодняшний день", callback_data="menu:calendar:today")],
        [InlineKeyboardButton(text="Посмотреть статистику", callback_data="menu:stats:month")],
    ])
