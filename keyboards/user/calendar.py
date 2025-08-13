from calendar import monthrange
from datetime import date
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from babel.dates import format_date
from services.activity_service import DONE, NOT_DONE

WEEKDAYS = ["П", "В", "С", "Ч", "П", "С", "В"]
WEEKEND_INDEXES = {5, 6}  # Суббота(5), Воскресенье(6) для datetime.weekday()


def _status_emoji(status: int) -> str:
    if status == DONE:
        return "✅"
    if status == NOT_DONE:
        return "❌"
    return "◻️"


def build_calendar(year: int, month: int, day_to_status: dict[int, int], today: date | None = None, locale: str = "ru_RU") -> InlineKeyboardMarkup:
    if today is None:
        today = date.today()

    kb_rows: list[list[InlineKeyboardButton]] = []
    # Заголовок (локализованный)
    title_date = date(year, month, 1)
    title = f"{format_date(title_date, format='LLLL yyyy', locale=locale).capitalize()}"
    kb_rows.append([InlineKeyboardButton(text=title, callback_data=f"cal:{year}:{month}:01:noop")])

    # Шапка дней недели
    kb_rows.append([InlineKeyboardButton(text=w, callback_data="cal:0:0:00:noop") for w in WEEKDAYS])

    first_weekday = date(year, month, 1).weekday()  # 0=Mon..6=Sun
    blanks = (first_weekday) % 7

    days_in_month = monthrange(year, month)[1]

    row: list[InlineKeyboardButton] = []
    for _ in range(blanks):
        row.append(InlineKeyboardButton(text=" ", callback_data="cal:0:0:00:noop"))

    for d in range(1, days_in_month + 1):
        status = day_to_status.get(d, 0)
        emoji = _status_emoji(status)
        the_date = date(year, month, d)
        is_today = (today.year == year and today.month == month and today.day == d)
        is_weekend = the_date.weekday() in WEEKEND_INDEXES
        marker = "·" if is_weekend else ""
        label_core = f"[{d}]" if is_today else f" {d}"
        label = f"{emoji}{label_core}{marker}"
        row.append(InlineKeyboardButton(text=label, callback_data=f"cal:{year}:{month}:{d:02d}:t"))
        if len(row) == 7:
            kb_rows.append(row)
            row = []
    if row:
        while len(row) < 7:
            row.append(InlineKeyboardButton(text=" ", callback_data="cal:0:0:00:noop"))
        kb_rows.append(row)

    # Навигация
    kb_rows.append([
        InlineKeyboardButton(text="◀️ Пред.", callback_data=f"cal:{year}:{month}:01:nav_prev"),
        InlineKeyboardButton(text="Сегодня", callback_data="cal:0:0:00:nav_today"),
        InlineKeyboardButton(text="След. ▶️", callback_data=f"cal:{year}:{month}:01:nav_next"),
    ])
    kb_rows.append([
        InlineKeyboardButton(text="🏠 Меню", callback_data="menu:home"),
        InlineKeyboardButton(text="↩️ Сбросить сегодня", callback_data="cal:0:0:00:reset_today"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb_rows) 