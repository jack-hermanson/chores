import logging
from datetime import datetime, timedelta

from main import DayOfWeekEnum


def get_next_date_with_same_day_of_week(day_of_week: DayOfWeekEnum, exclude_today=True,
                                        offset_days=0, relative_to_date: datetime = None):
    """
    Relative to today, get the next date that has the specified day of the week.
    It will exclude today unless you tell it not to.
    """
    start = relative_to_date or datetime.now()
    if (not exclude_today) and start.weekday() == day_of_week:
        # today is the day of the week we're looking for, and that's allowed
        # so go ahead and return it.
        return start + timedelta(days=offset_days)

    # if we cannot use today, or today is not the day of the week we want,
    # try adding a certain number of days (1-7) until we get to the desired day
    logging.debug(f"{int(day_of_week)} - {start.weekday()}")
    days_ahead = day_of_week - start.weekday()
    if days_ahead <= 0:
        # already happened
        days_ahead += 7
    return start + timedelta(days=days_ahead + offset_days)
