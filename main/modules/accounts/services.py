import logging

from main.modules.accounts.models import Account
from flask_login import current_user
from flask import request
from main import db
import uuid

from utils.get_ip import get_ip


def record_ip():
    """Record the IP address for this request"""
    if current_user.is_authenticated:
        account = Account.query.filter(Account.account_id == current_user.account_id).first_or_404()
        account.last_request_ip = get_ip(request)
        db.session.commit()


def reset_email_unsubscribe_token(account):
    logging.info(f"Resetting email_unsubscribe_token for account {account.name}/{account.account_id}")
    account.email_unsubscribe_token = uuid.uuid4().__str__()
    db.session.commit()


def unsubscribe_from_emails(email_unsubscribe_token: str):
    logging.info(f"Received unsubscribe token {email_unsubscribe_token}")
    account = Account.query.filter(Account.email_unsubscribe_token == email_unsubscribe_token).first_or_404()
    account.subscribed_to_emails = False
    db.session.commit()
    reset_email_unsubscribe_token(account)
