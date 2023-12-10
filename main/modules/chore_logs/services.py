import logging
from operator import and_

from utils.date_functions import get_next_date_with_same_day_of_week, get_next_date_with_same_number
from ..accounts.models import Account
from ..chores.RepeatTypeEnum import RepeatTypeEnum
from ..chores.models import Chore
from .models import ChoreLog
from flask_login import current_user
from datetime import datetime, timedelta
from main import db
from sqlalchemy import desc, not_
from . import helpers
from ..lists.models import List


def generate_next_chore_logs():
    """
    Generate next chore logs for the current user.
    Returns a list of chore logs for this user, ordered by due date ascending.
    """
    chores = db.session.query(Chore) \
        .join(Chore.list) \
        .join(List.accounts) \
        .filter(Account.account_id == current_user.account_id)

    for chore in chores:
        print(f"Checking chore {chore}")
        # for each chore get the open logs
        open_chore_logs = helpers.get_open_chore_logs(chore)

        # region guards
        # there should only be 0 or 1
        # if there are none, then make new logs for that chore
        if len(open_chore_logs) > 1:
            raise ValueError(f"Wtf, how are there {len(open_chore_logs)} logs open for this chore? {chore}\n"
                             f"{[(chore_log.completed_date is None) for chore_log in open_chore_logs]}")

        if len(open_chore_logs) == 1:
            # This one already has an open one
            logging.debug(f"Chore {chore} already has an open log. Skipping.")
            continue
        # endregion

        new_log_for_this_chore = ChoreLog()
        new_log_for_this_chore.chore = chore

        if chore.repeat_type == RepeatTypeEnum.DAYS:
            # add days to end of today
            new_log_for_this_chore.due_date = (datetime.now() + timedelta(days=chore.repeat_days)).date()
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            new_log_for_this_chore.due_date = get_next_date_with_same_day_of_week(
                new_log_for_this_chore.chore.repeat_day_of_week,
                exclude_today=False
            )
        elif chore.repeat_type == RepeatTypeEnum.NONE:
            logging.info(f"Chore with ID {chore.chore_id} does not repeat")
            new_log_for_this_chore.due_date = chore.one_time_due_date
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_MONTH:
            new_log_for_this_chore.due_date = get_next_date_with_same_number(chore.repeat_day_of_month)
        else:
            logging.error(f"Not a valid repeat type {chore.repeat_type}")
            new_log_for_this_chore.due_date = datetime.now().date()

        print(f"Created new log due {new_log_for_this_chore.due_date}")
        db.session.add(new_log_for_this_chore)
        db.session.commit()

    chore_logs_to_return = db.session.query(ChoreLog) \
        .join(ChoreLog.chore) \
        .join(Chore.list) \
        .join(List.accounts) \
        .filter(and_(Account.account_id == current_user.account_id, ChoreLog.completed_date.is_(None))) \
        .order_by(ChoreLog.due_date) \
        .all()

    return chore_logs_to_return


def complete(chore_log_id: int, stay_on_schedule: bool = False):
    print(f"complete chore log with id {chore_log_id}")

    # complete existing
    chore_log = ChoreLog.query.get_or_404(chore_log_id)
    if chore_log.completed_date is not None:
        raise ValueError(f"Chore Log was already completed {chore_log.completed_date}")

    chore_log.completed_date = datetime.now()
    chore_log.completed_by_account = current_user
    db.session.commit()

    if chore_log.chore.repeat_type == RepeatTypeEnum.NONE:
        return chore_log

    # create new
    new_chore_log = ChoreLog()
    new_chore_log.chore = chore_log.chore
    new_chore_log.due_date = chore_log.stay_on_schedule_next_due_date \
        if stay_on_schedule \
        else chore_log.normal_next_due_date

    db.session.add(new_chore_log)
    db.session.commit()

    return new_chore_log


def undo_completion(chore_log_id):
    chore_log = ChoreLog.query.get_or_404(chore_log_id)
    chore_id = chore_log.chore_id

    chore = chore_log.chore

    # Little bit different if it doesn't repeat
    if chore.repeat_type == RepeatTypeEnum.NONE:
        chore_log.completed_date = None
        db.session.commit()
        return chore_log

    chore.chore_logs.remove(chore_log)
    db.session.commit()
    db.session.refresh(chore)

    previous = ChoreLog.query \
        .filter(ChoreLog.chore_id == chore_id) \
        .order_by(desc(ChoreLog.completed_date)) \
        .first()

    if not previous:
        logging.info("Did not find a previous")
        db.session.commit()
        return None

    logging.info(f"Found previous {previous}; un-completing")
    previous.completed_date = None
    previous.completed_by_account = None
    db.session.commit()

    return previous
