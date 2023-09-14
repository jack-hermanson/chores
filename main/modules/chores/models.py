from main import db


class Chore(db.Model):
    chore_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(256), nullable=False, default="")

    # repeat every 14 days
    repeat_days = db.Column(db.Integer, nullable=True)

    # repeat every Sunday
    # use enum
    repeat_day_of_week = db.Column(db.Integer, nullable=True)

    # who is able to update/delete this task, who owns it
    owner_id = db.mapped_column(db.ForeignKey("account.account_id"), nullable=False)
    owner = db.relationship("Account", back_populates="chores")
