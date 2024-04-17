import logging
import time

from flask import render_template, url_for
from flask_mail import Message
from dotenv import load_dotenv
import os
from main import mail
from .models import AccountWithChoreLogs
from ..accounts.models import Account
from ..chore_logs.services import generate_next_chore_logs
from .pokemons import get_random_pokemon, get_info_for_pokemon

load_dotenv()

EMAIL_SENDER = (
    "Chores App",
    os.environ.get("EMAIL_FROM_ADDRESS")
)


def send_generic_email(
    recipients: list[str],
    subject,
    body,
    email_unsubscribe_token,
    html=False,
    greeting=None,
    reply_to=None,
    include_signature=True,
):
    message = Message(
        subject,
        sender=EMAIL_SENDER,
        reply_to=reply_to
    )

    if not html:
        message.body = body + "\n\n" + f"To unsubscribe, click here: {url_for('emails.unsubscribe', email_unsubscribe_token=email_unsubscribe_token)}"
    else:
        message.html = render_template(
            "emails/generic_email.html",
            body=body,
            greeting=greeting,
            include_signature=include_signature,
            closing_remarks=get_info_for_pokemon(get_random_pokemon()),
            email_unsubscribe_token=email_unsubscribe_token
        )

    message.recipients = recipients

    mail.send(message)


def get_users_who_want_reminder_emails():
    """
    Get a list of accounts that have subscribed_to_emails set to true
    """
    return Account.query.filter(Account.subscribed_to_emails.is_(True)).all()


def send_reminders_to_user(account_id: int):
    # first or 404 might not really make sense here, but whatever
    account = Account.query.filter(Account.account_id == account_id).first_or_404()
    account_and_chore_logs = get_chore_logs_for_user_to_remind_about(account)

    # to avoid "1 chores due"
    chore_or_chores = "chore" if len(account_and_chore_logs.chore_logs) == 1 else "chores"
    subject = f"Chores App: {len(account_and_chore_logs.chore_logs)} {chore_or_chores} to do"

    formatted_name = account.name.upper() if account.capitalize_name else account.name.capitalize()
    if len(account_and_chore_logs.chore_logs) > 0:
        logging.info(f"Sending reminder email to {account_and_chore_logs.account.name}")
        send_generic_email(
            recipients=[account.email],
            subject=subject,
            body=render_template(
                "emails/reminder-partial.html",
                chore_logs_to_remind=account_and_chore_logs.chore_logs,
                summary=f"You have <a href='{url_for('main.index', _external=True)}'>{len(account_and_chore_logs.chore_logs)} {chore_or_chores} due</a>:",
                user_name=formatted_name
            ),
            html=True,
            email_unsubscribe_token=account_and_chore_logs.account.email_unsubscribe_token
        )
    else:
        logging.info(f"No chore logs to remind {account_and_chore_logs.account.name} about")


def get_chore_logs_for_user_to_remind_about(user) -> AccountWithChoreLogs:
    """
    Get a list of chore logs that deserve a reminder for a specific user.
    They should be incomplete, due today, and the chore has reminders enabled.
    """
    chore_logs_to_remind = []
    next_chore_logs = generate_next_chore_logs(user=user)
    owned_next_chore_logs = [chore_log for chore_log in next_chore_logs if chore_log.chore.owner == user]
    for chore_log in owned_next_chore_logs:
        if chore_log.is_past_due and chore_log.chore.notifications_enabled:
            chore_logs_to_remind.append(chore_log)

    return AccountWithChoreLogs(
        account=user,
        chore_logs=chore_logs_to_remind
    )


def get_accounts_with_chore_logs_to_email() -> list[AccountWithChoreLogs]:
    """
    Get a list of AccountWithChoreLog
    """
    results: list[AccountWithChoreLogs] = []
    for user in get_users_who_want_reminder_emails():
        results.append(get_chore_logs_for_user_to_remind_about(user))
    return results
