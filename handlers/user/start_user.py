from datetime import date
from calendar import monthrange

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from services.activity_service import get_or_create_user, get_month_statuses, compute_streaks, summary, mark_today_done, top_users_by_streak, get_or_create_user_stats
from keyboards.user.start_user_keyboards import main_menu_kb
from keyboards.user.calendar import build_calendar
from supportiv_function.base import SupportiveFunctions


user_router = Router(name="user")


def _month_summary_text(user_id: int, year: int, month: int, done: int, not_done: int, not_marked: int, cur_streak: int, max_streak: int) -> str:
	total = done + not_done + not_marked
	percent = int((done / total) * 100) if total else 0
	month_name = date(year, month, 1).strftime("%B %Y")
	return (
		f"<b>{month_name}</b>\n"
		f"✅ {done} • ❌ {not_done} • ◻️ {not_marked}\n"
		f"Выполнено: {percent}% • Стрик: {cur_streak}/{max_streak}"
	)


@user_router.message(CommandStart())
async def start_cmd(msg: Message):
	user = await get_or_create_user(
		tg_id=msg.from_user.id,
		username=msg.from_user.username,
		nickname=(msg.from_user.full_name or msg.from_user.first_name),
	)
	await get_or_create_user_stats(user.id)
	await msg.answer(
		text=(
			"Привет! Это трекер прогресса.\n\n"
			"- Отмечай дни, когда занимался\n"
			"- Смотри календарь и статистику\n"
		),
		reply_markup=main_menu_kb(),
	)


@user_router.callback_query(F.data == "menu:home")
async def back_to_home(cb: CallbackQuery):
	await SupportiveFunctions.try_edit(
		cb,
		text=(
			"Привет! Это трекер прогресса.\n\n"
			"- Отмечай дни, когда занимался\n"
			"- Смотри календарь и статистику\n"
		),
		reply_markup=main_menu_kb(),
	)
	await cb.answer()


@user_router.callback_query(F.data == "menu:mark_today")
async def quick_mark_today(cb: CallbackQuery):
	await mark_today_done(cb.from_user.id)
	await cb.answer("Сегодня отмечено ✅")


@user_router.callback_query(F.data == "menu:top")
async def show_top(cb: CallbackQuery):
	stats = await top_users_by_streak(10)
	if not stats:
		text = "Пока нет данных для рейтинга"
	else:
		lines = []
		rank = 1
		user_place = None
		for s in stats:
			try:
				user = await s.user
				name = user.nickname or user.username or str(user.tg_id)
			except Exception:
				name = str(s.user_id)
			if user and user.tg_id == cb.from_user.id:
				user_place = rank
			lines.append(f"{rank}. {name} — стрик: {s.current_streak}, max: {s.max_streak}, ✅ {s.total_done}")
			rank += 1
		header = "<b>Топ 10 по стрику</b>"
		if user_place:
			header += f"\nВаше место: <b>{user_place}</b>"
		text = header + "\n\n" + "\n".join(lines)
	await SupportiveFunctions.try_edit(cb, text=text, reply_markup=main_menu_kb())
	await cb.answer()


@user_router.callback_query(F.data == "menu:calendar:today")
async def open_calendar_today(cb: CallbackQuery):
	today = date.today()
	user_tg_id = cb.from_user.id
	statuses = await get_month_statuses(user_tg_id, today.year, today.month)
	kb = build_calendar(today.year, today.month, statuses, today=today)

	# Статистика за месяц
	from services.activity_service import summary, compute_streaks
	done, not_done, not_marked = await summary(user_tg_id, date(today.year, today.month, 1), date(today.year, today.month, monthrange(today.year, today.month)[1]))
	cur, mx = await compute_streaks(user_tg_id, today)

	text = _month_summary_text(user_tg_id, today.year, today.month, done, not_done, not_marked, cur, mx)
	await SupportiveFunctions.try_edit(cb, text=text, reply_markup=kb)
	await cb.answer()


@user_router.callback_query(F.data.startswith("menu:stats:"))
async def open_stats(cb: CallbackQuery):
	today = date.today()
	period = cb.data.split(":")[-1]
	if period == "month":
		start = date(today.year, today.month, 1)
		from calendar import monthrange
		end = date(today.year, today.month, monthrange(today.year, today.month)[1])
	elif period == "7":
		from datetime import timedelta
		start = today - timedelta(days=6)
		end = today
	else:
		start = date(today.year, today.month, 1)
		from calendar import monthrange
		end = date(today.year, today.month, monthrange(today.year, today.month)[1])

	d, nd, nm = await summary(cb.from_user.id, start, end)
	cur, mx = await compute_streaks(cb.from_user.id, today)
	total = d + nd + nm
	percent = int((d / total) * 100) if total else 0
	text = (
		f"Статистика за период {start.strftime('%d.%m.%Y')} — {end.strftime('%d.%m.%Y')}\n\n"
		f"✅ {d} • ❌ {nd} • ◻️ {nm}\n"
		f"Выполнено: {percent}% • Стрик: {cur}/{mx}"
	)
	await SupportiveFunctions.try_edit(cb, text=text, reply_markup=main_menu_kb())
	await cb.answer()
