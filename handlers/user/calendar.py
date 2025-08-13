from datetime import date, timedelta
from calendar import monthrange

from aiogram import Router, F
from aiogram.types import CallbackQuery

from services.activity_service import get_month_statuses, cycle_day_status, compute_streaks, summary, get_or_create_user
from keyboards.user.calendar import build_calendar
from supportiv_function.base import SupportiveFunctions


calendar_router = Router(name="calendar")


def _move_month(year: int, month: int, delta: int) -> tuple[int, int]:
    m = month + delta
    y = year + (m - 1) // 12
    m = ((m - 1) % 12) + 1
    return y, m


@calendar_router.callback_query(F.data.startswith("cal:"))
async def handle_calendar(cb: CallbackQuery):
    parts = cb.data.split(":")  # cal:YYYY:MM:DD:action
    if len(parts) != 5:
        await cb.answer()
        return
    _, y, m, d, action = parts

    # Гарантируем наличие пользователя (иначе FK в Activity падает)
    await get_or_create_user(
        tg_id=cb.from_user.id,
        username=cb.from_user.username,
        nickname=(cb.from_user.full_name or cb.from_user.first_name),
    )

    today = date.today()

    if action == "noop":
        await cb.answer()
        return

    if action == "nav_today":
        year, month = today.year, today.month
    elif action == "nav_prev":
        year, month = _move_month(int(y), int(m), -1)
    elif action == "nav_next":
        year, month = _move_month(int(y), int(m), +1)
    else:
        year, month = int(y), int(m)

    # Обновление статуса дня
    if action == "t":
        day = int(d)
        target_date = date(year, month, day)
        if target_date > today:
            await cb.answer("Нельзя отмечать будущие даты", show_alert=False)
        else:
            await cycle_day_status(cb.from_user.id, target_date)

    # Стейт месяца
    statuses = await get_month_statuses(cb.from_user.id, year, month)
    kb = build_calendar(year, month, statuses, today=today)

    # Статистика месяца
    first = date(year, month, 1)
    last = date(year, month, monthrange(year, month)[1])
    d_done, d_not_done, d_not_marked = await summary(cb.from_user.id, first, last)
    cur, mx = await compute_streaks(cb.from_user.id, today)

    total = d_done + d_not_done + d_not_marked
    percent = int((d_done / total) * 100) if total else 0

    text = (
        f"<b>{first.strftime('%B %Y')}</b>\n"
        f"✅ {d_done} • ❌ {d_not_done} • ◻️ {d_not_marked}\n"
        f"Выполнено: {percent}% • Стрик: {cur}/{mx}"
    )

    await SupportiveFunctions.try_edit(cb, text=text, reply_markup=kb)
    await cb.answer() 