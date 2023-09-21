from flask import Blueprint, render_template
from main.modules.accounts.ClearanceEnum import ClearanceEnum
from main.utils.min_clearance import min_clearance
from .services import generate_next_chore_logs

chore_logs = Blueprint("chore_logs", __name__, url_prefix="/chore-logs")


@chore_logs.route("/generate-all")
@min_clearance(ClearanceEnum.NORMAL)
def generate_all():
    chores = generate_next_chore_logs()
    return [chore.__str__() for chore in chores], 201


@chore_logs.route("/")
@min_clearance(ClearanceEnum.NORMAL)
def index():
    chore_logs_list = generate_next_chore_logs()
    return render_template("chore_logs/index.html",
                           chore_logs_list=chore_logs_list)


@chore_logs.route("/complete")
@min_clearance(ClearanceEnum.NORMAL)
def complete(chore_id: int, stay_on_schedule: bool = False):
    pass