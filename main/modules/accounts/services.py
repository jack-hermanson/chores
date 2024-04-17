from main.modules.accounts.models import Account
from flask_login import current_user
from flask import request
from main import db

from utils.get_ip import get_ip


def record_ip():
    """Record the IP address for this request"""
    if current_user:
        account = Account.query.filter(Account.account_id == current_user.account_id).first_or_404()
        account.last_request_ip = get_ip(request)
        db.session.commit()
