from main import db
from main.modules.chores.RepeatTypeEnum import RepeatTypeEnum


class Chore(db.Model):
    chore_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(256), nullable=False, default="")

    # how should the repeat frequency be measured
    repeat_type = db.Column(db.Integer, nullable=False, default=RepeatTypeEnum.NONE)

    # repeat every 14 days
    repeat_days = db.Column(db.Integer, nullable=True)

    # repeat every Sunday
    # use enum
    repeat_day_of_week = db.Column(db.Integer, nullable=True)

    # who is able to update/delete this task, who owns it
    owner_id = db.mapped_column(db.ForeignKey("account.account_id"), nullable=False)
    owner = db.relationship("Account", back_populates="chores")

    chore_logs = db.relationship("ChoreLog", back_populates="chore", cascade="all, delete-orphan")

    list_id = db.mapped_column(db.ForeignKey("list.list_id"), nullable=False)
    list = db.relationship("List", back_populates="chores")

    # has_past_due_log  exists().where(CreditCard.user_id == id)

    def __repr__(self):
        return f"<{self.title}, {self.chore_id}, {self.owner.name}, {str(RepeatTypeEnum(self.repeat_type))}>"
