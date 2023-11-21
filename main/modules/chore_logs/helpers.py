from sqlalchemy import and_

from main.modules.chore_logs.models import ChoreLog
from main.modules.chores.models import Chore


def get_open_chore_logs(chore: Chore):
    """
    Get a list of open chore logs for a chore
    """
    open_chore_logs = ChoreLog.query.filter(
        and_(ChoreLog.chore == chore, ChoreLog.completed_date.is_(None))) \
        .all()
    return open_chore_logs



