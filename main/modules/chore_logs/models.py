from __future__ import annotations

from typing import ClassVar

from main import db
from datetime import datetime
from sqlalchemy import and_, desc

from main.modules.accounts.models import Account
from main.modules.chores.RepeatTypeEnum import RepeatTypeEnum
from main.modules.chores.models import Chore


class ChoreLog(db.Model):
    chore_log_id = db.Column(db.Integer, primary_key=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    is_past_due = db.column_property((completed_date is None) and due_date < datetime.now())
    is_complete = db.column_property(completed_date.is_not(None))

    completed_by_account_id = db.mapped_column(
        db.ForeignKey("account.account_id"), nullable=True
    )
    completed_by_account = db.relationship("Account", back_populates="chore_logs")

    chore_id = db.mapped_column(
        db.ForeignKey("chore.chore_id"), nullable=False
    )
    chore = db.relationship("Chore", back_populates="chore_logs")

    def __repr__(self):
        return f"<{self.chore.title}, {self.chore_log_id}, {str(RepeatTypeEnum(self.chore.repeat_type))}, " \
               f"{self.due_date}, past_due: {self.is_past_due}>"

    def get_previous(self):
        prev = ChoreLog.query. \
            filter(and_(ChoreLog.chore == self.chore, ChoreLog.is_complete.is_(True))) \
            .order_by(desc(ChoreLog.completed_date)) \
            .first()
        return prev

    def as_dict(self):
        return {
            "chore": self.chore.title,
            "chore_log_id": self.chore_log_id,
            "repeat_type": str(RepeatTypeEnum(self.chore.repeat_type)),
            "due_date": self.due_date,
            "past_due": self.is_past_due,
            "completed_date": self.completed_date
        }


class ChoreLogViewModel:
    def __init__(self, chore_log: ChoreLog):
        self.chore_log_id = chore_log.chore_log_id
        self.completed_date = chore_log.completed_date
        self.due_date = chore_log.due_date
        self.is_past_due = chore_log.is_past_due
        self.is_complete = chore_log.is_complete
        self.completed_by_account_id = chore_log.completed_by_account_id
        self.completed_by_account = chore_log.completed_by_account
        self.chore_id = chore_log.chore_id
        self.chore = chore_log.chore
        self.previous = chore_log.get_previous()

    chore_log_id: int
    completed_date: datetime | None
    due_date: datetime
    is_past_due: bool
    is_complete: bool
    completed_by_account_id: int
    completed_by_account: Account
    chore_id: int
    chore: Chore
    previous: ChoreLog
