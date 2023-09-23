import logging

from ..accounts.models import Account
from ..chores.RepeatTypeEnum import RepeatTypeEnum
from ..chores.models import Chore
from .models import ChoreLog
from flask_login import current_user
from datetime import datetime, timedelta
from main import db
from sqlalchemy import and_, desc, text
from . import helpers


def generate_next_chore_logs():
    """
    Generate next chore logs for the current user.
    Returns a list of chore logs for this user, ordered by due date ascending
    """
    chores = Chore.query.filter(Chore.owner == current_user).all()

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
            print(f"Chore {chore} already has an open log. Skipping.")
            continue
        # endregion

        new_log_for_this_chore = ChoreLog()
        new_log_for_this_chore.chore = chore

        if chore.repeat_type == RepeatTypeEnum.DAYS:
            # if we're past due, add days to end of today
            # add number of days to the end
            new_log_for_this_chore.due_date = datetime.now() + timedelta(days=chore.repeat_days)
        else:
            # todo
            new_log_for_this_chore.due_date = datetime.now()

        print(f"Created new log due {new_log_for_this_chore.due_date}")
        db.session.add(new_log_for_this_chore)
        db.session.commit()

    chore_logs_to_return = ChoreLog.query.join(ChoreLog.chore) \
        .filter(and_(Chore.owner == current_user, ChoreLog.completed_date.is_(None))).order_by(ChoreLog.due_date).all()

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
        # done forever
        return None

    # create new
    new_chore_log = ChoreLog()
    new_chore_log.chore = chore_log.chore
    if chore_log.chore.repeat_type == RepeatTypeEnum.DAYS:
        new_chore_log.due_date = datetime.now() + timedelta(days=chore_log.chore.repeat_days)
    elif chore_log.chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
        new_chore_log.due_date = helpers.get_next_date_with_same_day_of_week(
            new_chore_log.chore.repeat_day_of_week,
            exclude_today=True
        )
    else:  # should never happen
        raise ValueError(f"Invalid repeat type {chore_log.chore.repeat_type}")

    db.session.add(new_chore_log)
    db.session.commit()

    return new_chore_log


def undo_completion(chore_log_id):

    chore_log = ChoreLog.query.get_or_404(chore_log_id)
    chore_id = chore_log.chore_id

    chore = chore_log.chore
    chore.chore_logs.remove(chore_log)
    db.session.commit()
    db.session.refresh(chore)
    # db.session.flush()

    previous = ChoreLog.query \
        .filter(ChoreLog.chore_id == chore_id)\
        .order_by(desc(ChoreLog.completed_date))\
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





    # previous_chore_log_query = (db.session.query(ChoreLog, Chore, Account)
    #                             .select_from(ChoreLog)
    #                             .join(Chore).join(Account).filter(
    #     and_(
    #         ChoreLog.chore == chore_log.chore,
    #         ChoreLog.is_complete.is_(True),
    #         ChoreLog.chore_log_id != chore_log_id
    #     )
    # ).order_by(desc(ChoreLog.completed_date)).first())
    #
    # if not previous_chore_log_query:
    #     logging.info("No previous chore log for this one")
    #     return None
    #
    # # first in tuple
    # previous_chore_log = previous_chore_log_query[0]
    #
    # if previous_chore_log:
    #     logging.info(f"Found previous chore log with ID {previous_chore_log.chore_log_id}")
    #     previous_chore_log.completed_date = None
    #     previous_chore_log.completed_by_account = None
    #     db.session.commit()
    #
    # previous_chore_log_id = previous_chore_log.chore_log_id
    # previous_chore_log = (ChoreLog.query
    #                       .filter(ChoreLog.chore_log_id == previous_chore_log_id)
    #                       .first())
    #
    # logging.info("Deleting the original chore log now")
    # db.session.delete(chore_log)
    # logging.info("Deleted it")
    # db.session.commit()
    #
    # if not previous_chore_log:
    #     logging.fatal("WHAT THE FUCK")
    # return previous_chore_log
