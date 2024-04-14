from flask import Blueprint
from .services import send_generic_email
from datetime import datetime
from flask import request

emails = Blueprint("emails", __name__, url_prefix="/emails")


@emails.route("/testing")
def testing():
    send_generic_email(
        recipients=[
            "jack.hermanson@live.com"
        ],
        subject=f"This is a test from {datetime.now().isoformat()}",
        body=f"Well you made it this far from {get_ip()}.",
        html=True,
        greeting="Uh hi?",
        include_signature=True,
        sleep=False
    )
    return "You did it", 202


def get_ip():
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr
