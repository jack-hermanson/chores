import time

from flask import render_template
from flask_mail import Message
from dotenv import load_dotenv
import os
from main import mail

load_dotenv()


def send_generic_email(
    recipients: list[str],
    subject,
    body,
    html=False,
    greeting=None,
    sleep=True,
    reply_to=None,
    include_signature=True
):
    message = Message(
        subject,
        sender=(
            "Chores App",
            os.environ.get("EMAIL_FROM_ADDRESS")
        ),
        reply_to=reply_to
    )

    if not html:
        message.body = body
    else:
        message.html = render_template(
            "emails/generic_email.html",
            body=body,
            greeting=greeting,
            include_signature=include_signature
        )

    message.recipients = recipients

    if sleep:
        time.sleep(2)

    mail.send(message)
