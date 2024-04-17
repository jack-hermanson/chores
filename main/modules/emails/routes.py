from flask import Blueprint

from .models import AccountWithChoreLogs
from .services import send_reminders_to_user, send_generic_email, get_users_who_want_reminder_emails, get_chore_logs_for_user_to_remind_about
from datetime import datetime
from flask import request
import os

emails = Blueprint("emails", __name__, url_prefix="/emails")


def request_has_valid_api_key_header():
    """Check if the API key header is valid"""
    return os.environ.get("API_KEY") == request.headers.get("X-API-KEY")


@emails.route("/send-reminders", methods=["POST"])
def send_reminders():
    """Actually send the reminder for a single account ID"""
    if not request_has_valid_api_key_header():
        return "Invalid token", 401
    # request.json: parsed JSON data. The request must have the application/json content type,
    # or use request.get_json(force=True) to ignore the content type.
    account_id = request.json.get("account_id")
    try:
        send_reminders_to_user(account_id)
        return "Sent!"
    except Exception as e:
        return str(e), 500
