from __future__ import annotations
from main import db
from datetime import datetime, timedelta
from sqlalchemy import and_, desc, not_

from utils.date_functions import get_next_date_with_same_day_of_week, extract_date
from main.modules.chores.RepeatTypeEnum import RepeatTypeEnum


class ChoreLog(db.Model):
    chore_log_id = db.Column(db.Integer, primary_key=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    # is_past_due = db.column_property(and_((completed_date is None), due_date < datetime.now()))
    # is_complete = db.column_property(completed_date.is_not(None))

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

    @property
    def previous(self):
        prev = ChoreLog.query. \
            filter(and_(ChoreLog.chore == self.chore, not_(ChoreLog.completed_date.is_(None)))) \
            .order_by(desc(ChoreLog.completed_date)) \
            .first()
        return prev

    @property
    def is_complete(self):
        return self.completed_date is not None

    @property
    def is_past_due(self):
        return self.due_date < datetime.now()

    @property
    def stay_on_schedule_next_due_date(self):
        """The next due date after this one if we select complete stay on schedule"""
        if self.chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            # if it's a weekly thing, and we're staying on schedule, find the next of the repeat day closest to due date
            return get_next_date_with_same_day_of_week(self.chore.repeat_day_of_week, relative_to_date=self.due_date)
        if self.chore.repeat_type == RepeatTypeEnum.DAYS:
            # if it repeats every certain # of days, add that number of days to the due date
            return (self.due_date + timedelta(days=self.chore.repeat_days)).date()
        if self.chore.repeat_type == RepeatTypeEnum.NONE:
            return None

    @property
    def normal_next_due_date(self):
        """The next due date relative to today, not trying to stick to any particular schedule"""
        if self.chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            # this could be refactored but fuck it for now it's fine

            next_date_with_same_day_of_week = get_next_date_with_same_day_of_week(self.chore.repeat_day_of_week)

            # if it's overdue, bring it up to the next day of the week relative to today
            if self.is_past_due:
                return next_date_with_same_day_of_week

            # if it's not overdue, then it's early or on time, so add a week to the next time that date occurs

            # first get the next date with that day of week relative to today
            next_date = get_next_date_with_same_day_of_week(self.chore.repeat_day_of_week) + timedelta(7)

            # then make sure that is not the due date for this one, which we just completed
            # that would make it infinitely staying on the same date
            # if that's the case, add 7 days
            if extract_date(next_date) == extract_date(self.due_date):
                return next_date + timedelta(days=7)

            return next_date

        if self.chore.repeat_type == RepeatTypeEnum.DAYS:
            # if it repeats every certain # of days, add that number to today
            next_date = (datetime.now() + timedelta(days=self.chore.repeat_days)).date()

            # if we add this # of days, and we get the same due date, that's not gonna work,
            # so add another # of those days
            if extract_date(next_date) == extract_date(self.due_date):
                return next_date + timedelta(days=self.chore.repeat_days)

            return next_date
        if self.chore.repeat_type == RepeatTypeEnum.NONE:
            return None

    def as_dict(self):
        return {
            "chore": self.chore.title,
            "chore_log_id": self.chore_log_id,
            "repeat_type": str(RepeatTypeEnum(self.chore.repeat_type)),
            "due_date": self.due_date,
            "past_due": self.is_past_due,
            "completed_date": self.completed_date
        }
