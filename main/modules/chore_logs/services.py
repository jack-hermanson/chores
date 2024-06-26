from datetime import datetime, timedelta

from flask_login import current_user
from sqlalchemy import desc, not_, or_, and_, func

from main import db, logger
from utils.date_functions import get_next_date_with_same_day_of_week, get_next_date_with_same_number
from . import helpers
from .models import ChoreLog
from ..accounts.models import Account
from ..chores.RepeatTypeEnum import RepeatTypeEnum
from ..chores.models import Chore
from ..lists.models import List
from statistics import mean


def generate_next_chore_logs(user=current_user, search_text="", show_archived=False,
                             list_ids: list[int] or None = None):
    """
    Generate next chore logs for a given user, likely the current user.
    Returns a list of chore logs for this user, ordered by due date ascending.
    The use case for passing in a specific user is generating chore logs for a user for reminder emails.
    """
    logger.debug("Generating next chore logs")
    if list_ids is None:
        list_ids = [list_.list_id for list_ in user.lists]

    chores = db.session.query(Chore) \
        .join(Chore.list) \
        .join(List.accounts) \
        .filter(Account.account_id == user.account_id)

    for chore in chores:
        logger.debug(f"Checking chore {chore}")
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
            logger.debug(f"Chore {chore} already has an open log. Skipping.")
            continue
        # endregion

        new_log_for_this_chore = ChoreLog()

        # Chore does not repeat
        if chore.repeat_type == RepeatTypeEnum.NONE:
            logger.info(f"Chore with ID {chore.chore_id} ({chore.title}) does not repeat")
            # since the chore doesn't repeat, we really only need to generate a log once
            if len(chore.chore_logs):
                # there already is a chore log
                continue
            else:
                # create a new one
                new_log_for_this_chore.due_date = chore.one_time_due_date

        # Chore repeats by day
        elif chore.repeat_type == RepeatTypeEnum.DAYS:
            # add days to end of today
            new_log_for_this_chore.due_date = (datetime.now() + timedelta(days=chore.repeat_days)).date()

        # Day of the week
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            new_log_for_this_chore.due_date = get_next_date_with_same_day_of_week(
                chore.repeat_day_of_week,
                exclude_today=False
            )

        # Day of the month
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_MONTH:
            new_log_for_this_chore.due_date = get_next_date_with_same_number(chore.repeat_day_of_month)
        else:
            logger.error(f"Not a valid repeat type {chore.repeat_type}")
            new_log_for_this_chore.due_date = datetime.now().date()

        logger.info(f"Created new log for {chore} due {new_log_for_this_chore.due_date}")

        chore.chore_logs.append(new_log_for_this_chore)
        db.session.add(new_log_for_this_chore)
        db.session.commit()

    chore_logs_to_return = db.session.query(ChoreLog) \
        .join(ChoreLog.chore) \
        .join(Chore.list) \
        .join(List.accounts) \
        .filter(
        and_(
            # search term matches
            # commented out because we only want to search for title
            # or_(
            Chore.title.ilike(f"%{search_text}%"),
            #     Chore.description.ilike(f"%{search_text}%")
            # ),
            # and
            # chore in list that this user belongs to

            # this was removed because of stupid lack of short-circuiting in boolean expressions
            # so in_(list_ids) was evaluated even if list_ids is None.
            # or_(
            #     # either the caller did not specify list ids
            #     # and this list is connected to user
            #     and_(
            #         list_ids is None,
            #         List.accounts.contains(user)
            #     ),
            #     # or the caller did specify list ids
            #     # and this list is one that the user asked for
            #     # and this list is connected to user
            #     and_(
            #         list_ids is not None,
            #         List.accounts.contains(user),
            #         List.list_id.in_(list_ids)
            #     )
            # ),

            and_(
                List.accounts.contains(user),
                List.list_id.in_(list_ids)
            ),

            # List.accounts.contains(user),
            # and
            or_(
                # this is a repeating chore and chore_log is incomplete
                and_(
                    Chore.repeat_type != RepeatTypeEnum.NONE,
                    ChoreLog.completed_date.is_(None)
                ),
                # or
                and_(
                    # this is a non-repeating chore
                    Chore.repeat_type == RepeatTypeEnum.NONE,
                    # and
                    or_(
                        # it's unarchived
                        not_(Chore.archived),
                        # or we want to show archived
                        show_archived
                    )
                )
            )
        )
    ) \
        .order_by(ChoreLog.due_date) \
        .all()

    return chore_logs_to_return


def complete(chore_log_id: int, stay_on_schedule: bool = False):
    logger.info(f"complete chore log with id {chore_log_id}")

    # complete existing
    chore_log = ChoreLog.query.get_or_404(chore_log_id)
    if chore_log.completed_date is not None and chore_log.chore.archived:
        raise ValueError(
            f"Chore Log was already completed on {chore_log.completed_date} and archived (chore log ID {chore_log_id}")

    # archive completed
    if chore_log.completed_date and not chore_log.chore.archived:
        logger.info(f"Archiving {chore_log.chore.title}")
        chore_log.chore.archived = True
        db.session.commit()
        return chore_log

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
        chore_log.chore.archived = False
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
        logger.info("Did not find a previous")
        db.session.commit()
        return None

    logger.info(f"Found previous {previous}; un-completing")
    previous.completed_date = None
    previous.completed_by_account = None
    db.session.commit()

    return previous


def get_previous_logs(chore_id: int, page: int):
    chore_logs = (ChoreLog.query
                  .filter(and_(ChoreLog.chore_id == chore_id,
                               ChoreLog.completed_date.is_not(None)))
                  .order_by(ChoreLog.completed_date.desc())
                  .paginate(page=page, per_page=10))
    return chore_logs


def get_average_timeliness(chore_id):
    logger.debug("Getting average timeliness for chore with ID", chore_id)
    chore_logs = (
        ChoreLog.query.filter(
            and_(
                ChoreLog.chore_id == chore_id,
                ChoreLog.completed_date.is_not(None)
            )
        ).all()
    )
    if len(chore_logs) == 0:
        return 0
    differences_in_days = [
        (chore_log.completed_date - chore_log.due_date).days
        for chore_log in chore_logs
    ]
    average_timeliness = mean(differences_in_days)
    return average_timeliness

    # for debugging
    # return [
    #     {
    #         "chore_log_id": chore_log.chore_log_id,
    #         "due_date": chore_log.due_date,
    #         "completed_date": chore_log.completed_date,
    #         "difference": str(chore_log.completed_date - chore_log.due_date),
    #         "was_late": (chore_log.completed_date - chore_log.due_date).days > 0,
    #         "was_early": (chore_log.completed_date - chore_log.due_date).days < 0,
    #         "was_on_time": (chore_log.completed_date - chore_log.due_date).days == 0,
    #         "x_dif_days": (chore_log.completed_date - chore_log.due_date).days
    #     }
    #     for chore_log in chore_logs
    # ]
