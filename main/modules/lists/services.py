import logging

from flask_login import current_user

from main.modules.accounts.models import Account


def get_user_lists():
    results = (Account.query.filter(Account.account_id == current_user.account_id)
               .first_or_404().lists)
    logging.info(f"current_user: {current_user}")
    logging.info(f"Results: {results}")
    return results
