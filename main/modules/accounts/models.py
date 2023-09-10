from main import db, login_manager
from flask_login import UserMixin
from .ClearanceEnum import ClearanceEnum
from sqlalchemy.sql import func


@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))


class Account(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    clearance = db.Column(db.Integer, default=ClearanceEnum.UNVERIFIED)
    email = db.Column(db.String, unique=True, nullable=False)
    join_date = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
