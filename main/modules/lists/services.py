import logging

from flask_login import current_user

from main.modules.accounts.models import Account


def get_user_lists():
    results = (Account.query.filter(Account.account_id == current_user.account_id)
               .first_or_404().lists)
    logging.info(f"current_user: {current_user}")
    logging.info(f"Results: {results}")
    return results


# helper method to get rid of warning about duplicated code on create/edit
def set_list_values(new_list, form):
    new_list.title = form.title.data
    new_list.description = form.description.data

    accounts = []
    for account_id in form.accounts.data + [current_user.account_id]:
        accounts.append(Account.query.filter(Account.account_id == account_id).first())
    new_list.accounts = accounts
    return new_list
