from flask import Blueprint
from json import dumps,load

from main.modules.accounts.ClearanceEnum import ClearanceEnum
from main.utils.min_clearance import min_clearance
from .services import generate_next_chore_logs

chore_logs = Blueprint("chore_logs", __name__, url_prefix="/chore-logs")


@chore_logs.route("/generate-all")
@min_clearance(ClearanceEnum.NORMAL)
def generate_all():
    chores = generate_next_chore_logs()
    return [chore.__str__() for chore in chores], 201
