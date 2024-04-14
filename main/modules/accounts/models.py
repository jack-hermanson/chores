from flask_login import UserMixin
from sqlalchemy.sql import func

from main import db, login_manager
from .ClearanceEnum import ClearanceEnum
from ..lists.models import list_account


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))


class Account(db.Model, UserMixin):
    def get_id(self):
        return self.account_id

    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    clearance = db.Column(db.Integer, default=ClearanceEnum.UNVERIFIED)
    email = db.Column(db.String, unique=True, nullable=False)
    join_date = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    capitalize_name = db.Column(db.Boolean, nullable=False, default=False)
    subscribed_to_emails = db.Column(db.Boolean, nullable=False, default=True)

    # relationship
    lists = db.relationship("List", secondary=list_account, back_populates="accounts")
    chores = db.relationship("Chore", back_populates="owner", cascade="all, delete-orphan")
    chore_logs = db.relationship("ChoreLog", back_populates="completed_by_account", cascade="all, delete-orphan")
    invitations = db.relationship("Invitation", back_populates="recipient", cascade="all, delete-orphan")
    owned_lists = db.relationship("List", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<{self.name}, {self.account_id}>"

    @property
    def formatted_name(self):
        if self.capitalize_name:
            return self.name.upper()
        else:
            return self.name.title()