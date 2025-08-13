from calendar import monthrange
from datetime import date
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.activity_service import DONE, NOT_DONE

WEEKDAYS = ["П", "В", "С", "Ч", "П", "С", "В"]


def _status_emoji(status: int) -> str:
    if status == DONE:
        return "✅"
    if status == NOT_DONE:
        return "❌"
    return "◻️"


def build_calendar(year: int, month: int, day_to_status: dict[int, int], today: date | None = None) -> InlineKeyboardMarkup:
    if today is None:
        today = date.today()

    kb_rows: list[list[InlineKeyboardButton]] = []
    # Заголовок
    title = f"{today.strftime('%B') if (today.year == year and today.month == month) else date(year, month, 1).strftime('%B')} {year}"
    kb_rows.append([InlineKeyboardButton(text=title, callback_data=f"cal:{year}:{month}:01:noop")])

    # Шапка дней недели
    kb_rows.append([InlineKeyboardButton(text=w, callback_data="cal:0:0:00:noop") for w in WEEKDAYS])

    first_weekday = date(year, month, 1).weekday()  # 0=Mon..6=Sun
    # Нужна локализация Пн..Вс: у нас WEEKDAYS уже П..В.., а weekday() Mon=0, значит смещение
    # Рассчитаем отступы: в нашей шапке Пн первый, так что first_weekday уже корректен
    blanks = (first_weekday) % 7

    days_in_month = monthrange(year, month)[1]

    # Первая неделя с отступами
    row: list[InlineKeyboardButton] = []
    for _ in range(blanks):
        row.append(InlineKeyboardButton(text=" ", callback_data="cal:0:0:00:noop"))

    for d in range(1, days_in_month + 1):
        status = day_to_status.get(d, 0)
        emoji = _status_emoji(status)
        label = f"{emoji}{'[' + str(d) + ']' if (today.year == year and today.month == month and today.day == d) else ' ' + str(d)}"
        row.append(InlineKeyboardButton(text=label, callback_data=f"cal:{year}:{month}:{d:02d}:t"))
        if len(row) == 7:
            kb_rows.append(row)
            row = []
    if row:
        # добиваем пустыми
        while len(row) < 7:
            row.append(InlineKeyboardButton(text=" ", callback_data="cal:0:0:00:noop"))
        kb_rows.append(row)

    # Навигация
    kb_rows.append([
        InlineKeyboardButton(text="◀️ Пред.", callback_data=f"cal:{year}:{month}:01:nav_prev"),
        InlineKeyboardButton(text="Сегодня", callback_data="cal:0:0:00:nav_today"),
        InlineKeyboardButton(text="След. ▶️", callback_data=f"cal:{year}:{month}:01:nav_next"),
    ])
    # Возврат в главное меню
    kb_rows.append([
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu:home"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb_rows) 