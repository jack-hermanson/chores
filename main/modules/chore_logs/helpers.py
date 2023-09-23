import logging

from sqlalchemy import and_
from datetime import datetime, timedelta

from main.modules.chore_logs.models import ChoreLog
from main.modules.chores.models import Chore
from main.utils.DateTimeEnums import DayOfWeekEnum


def get_open_chore_logs(chore: Chore):
    """
    Get a list of open chore logs for a chore
    """
    open_chore_logs = ChoreLog.query.filter(
        and_(ChoreLog.chore == chore, ChoreLog.completed_date.is_(None))) \
        .all()
    return open_chore_logs


def get_next_date_with_same_day_of_week(day_of_week: DayOfWeekEnum, exclude_today=True,
                                        offset_days=0):
    """
    Relative to today, get the next date that has the specified day of the week.
    It will exclude today unless you tell it not to.
    """
    now = datetime.now()
    if (not exclude_today) and now.weekday() == day_of_week:
        # today is the day of the week we're looking for, and that's allowed
        # so go ahead and return it.
        return now + timedelta(days=offset_days)

    # if we cannot use today, or today is not the day of the week we want,
    # try adding a certain number of days (1-7) until we get to the desired day
    logging.debug(f"{int(day_of_week)} - {now.weekday()}")
    days_ahead = day_of_week - now.weekday()
    if days_ahead <= 0:
        # already happened
        days_ahead += 7
    return now + timedelta(days=days_ahead + offset_days)



