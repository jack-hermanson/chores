from ..chores.RepeatTypeEnum import RepeatTypeEnum
from ..chores.models import Chore
from .models import ChoreLog
from flask_login import current_user
from datetime import datetime, timedelta
from main import db


def generate_next_chore_logs():
    """
    Generate next chore logs for the current user.
    Returns a list of chore logs for this user, ordered by due date ascending
    """
    chores = Chore.query.filter(Chore.owner == current_user).all()

    for chore in chores:
        print(f"Checking chore {chore}")
        # for each chore get the open logs
        open_chore_logs = ChoreLog.query.filter(ChoreLog.chore == chore and
                                                ChoreLog.completed_date is None).all()

        # there should only be 0 or 1
        # if there are none, then make new logs for that chore
        if len(open_chore_logs) > 1:
            print(chore)
            raise ValueError(f"Wtf, how are there {len(open_chore_logs)} logs open for this chore?")

        if len(open_chore_logs) == 1:
            # This one already has an open one
            print(f"Chore {chore} already has an open log. Skipping.")
            continue

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

    return ChoreLog.query.join(ChoreLog.chore).filter(Chore.owner == current_user).order_by(ChoreLog.due_date).all()
