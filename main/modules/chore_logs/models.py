from main import db
from sqlalchemy import func


class ChoreLog(db.Model):
    chore_log_id = db.Column(db.Integer, primary_key=True)
    completed_date = db.Column(db.DateTime, nullable=True)

    completed_by_account_id = db.mapped_column(
        db.ForeignKey("account.account_id"), nullable=True
    )
    completed_by_account = db.relationship("Account", back_populates="chore_logs")

    chore_id = db.mapped_column(
        db.ForeignKey("chore.chore_id"), nullable=False
    )
    chore = db.relationship("Chore", back_populates="chore_logs")
