from datetime import date, datetime, timedelta
from calendar import monthrange
from typing import Dict, Tuple, List

from tortoise.expressions import Q

from database.models.user import User
from database.models.activity import Activity
from database.models.user_stats import UserStats


DONE = 1
NOT_DONE = -1


async def get_or_create_user(tg_id: int, username: str | None, nickname: str | None) -> User:
    user, _ = await User.get_or_create(tg_id=tg_id, defaults={
        "username": username,
        "nickname": nickname,
    })
    need_update = False
    if username and user.username != username:
        user.username = username
        need_update = True
    if nickname and user.nickname != nickname:
        user.nickname = nickname
        need_update = True
    if need_update:
        await user.save()
    # Статистику гарантируем
    await get_or_create_user_stats(user.id)
    return user


async def get_or_create_user_stats(user_id: int) -> UserStats:
    stats, _ = await UserStats.get_or_create(user_id=user_id)
    return stats


async def get_month_statuses(user_tg_id: int, year: int, month: int) -> Dict[int, int]:
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    records = await Activity.filter(user__tg_id=user_tg_id, date__gte=start, date__lte=end).all()
    by_day: Dict[int, int] = {}
    for rec in records:
        by_day[rec.date.day] = rec.status
    return by_day


async def cycle_day_status(user_tg_id: int, target_date: date) -> int:
    rec = await Activity.filter(user__tg_id=user_tg_id, date=target_date).first()
    if rec is None:
        user = await User.get(tg_id=user_tg_id)
        rec = await Activity.create(user_id=user.id, date=target_date, status=DONE)
        await recompute_and_save_stats(user.id)
        return rec.status
    if rec.status == DONE:
        rec.status = NOT_DONE
    elif rec.status == NOT_DONE:
        await rec.delete()
        await recompute_and_save_stats(rec.user_id)
        return 0
    await rec.save()
    await recompute_and_save_stats(rec.user_id)
    return rec.status


async def set_day_status(user_tg_id: int, target_date: date, status: int) -> None:
    rec = await Activity.filter(user__tg_id=user_tg_id, date=target_date).first()
    if status == 0:
        if rec:
            user_id = rec.user_id
            await rec.delete()
            await recompute_and_save_stats(user_id)
        return
    if rec is None:
        user = await User.get(tg_id=user_tg_id)
        await Activity.create(user_id=user.id, date=target_date, status=status)
        await recompute_and_save_stats(user.id)
    else:
        rec.status = status
        await rec.save()
        await recompute_and_save_stats(rec.user_id)


async def compute_streaks(user_tg_id: int, up_to: date | None = None) -> Tuple[int, int]:
    if up_to is None:
        up_to = date.today()
    start = up_to - timedelta(days=400)
    records = await Activity.filter(user__tg_id=user_tg_id, date__gte=start, date__lte=up_to).all()
    done_days = {r.date for r in records if r.status == DONE}
    cur = 0
    d = up_to
    while d in done_days:
        cur += 1
        d -= timedelta(days=1)
    max_streak = 0
    visited = set()
    for day in sorted(done_days):
        if day in visited:
            continue
        length = 1
        next_day = day + timedelta(days=1)
        while next_day in done_days:
            visited.add(next_day)
            length += 1
            next_day += timedelta(days=1)
        if length > max_streak:
            max_streak = length
    return cur, max_streak


async def summary(user_tg_id: int, start_date: date, end_date: date) -> Tuple[int, int, int]:
    records = await Activity.filter(user__tg_id=user_tg_id, date__gte=start_date, date__lte=end_date).all()
    total_days = (end_date - start_date).days + 1
    done = sum(1 for r in records if r.status == DONE)
    not_done = sum(1 for r in records if r.status == NOT_DONE)
    marked = done + not_done
    not_marked = max(0, total_days - marked)
    return done, not_done, not_marked


async def recompute_and_save_stats(user_id: int) -> None:
    user = await User.get(id=user_id)
    done = await Activity.filter(user_id=user_id, status=DONE).count()
    not_done = await Activity.filter(user_id=user_id, status=NOT_DONE).count()
    cur, mx = await compute_streaks(user.tg_id)
    stats = await get_or_create_user_stats(user_id)
    stats.total_done = done
    stats.total_not_done = not_done
    stats.current_streak = cur
    stats.max_streak = max(stats.max_streak, mx)
    await stats.save()


async def mark_today_done(user_tg_id: int) -> None:
    today = date.today()
    await set_day_status(user_tg_id, today, DONE)


async def top_users_by_streak(limit: int = 10) -> List[UserStats]:
    return await UserStats.all().order_by("-current_streak", "-max_streak", "-total_done").limit(limit) 