from main import db
from sqlalchemy import func
from datetime import datetime

from main.modules.chores.RepeatTypeEnum import RepeatTypeEnum


class ChoreLog(db.Model):
    chore_log_id = db.Column(db.Integer, primary_key=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    is_past_due = db.column_property(due_date < datetime.now())

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
