from flask import Blueprint

from main.modules.accounts.models import Account
from main.modules.accounts.services import reset_email_unsubscribe_token

single_use_endpoints = Blueprint("single_use_endpoints", __name__, url_prefix="/single-use-endpoints")


"""
These are endpoints that should be hit once, to make a change, then removed.
"""


@single_use_endpoints.route("/email-tokens")
def set_email_tokens():
    """
    This sets everyone's email token so it's not "placeholder"
    """
    accounts = Account.query.all()
    for account in accounts:
        reset_email_unsubscribe_token(account)
    return "done", 200
