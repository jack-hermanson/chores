from flask import Blueprint, render_template

from main.modules.accounts.ClearanceEnum import ClearanceEnum
from main.utils.min_clearance import min_clearance

chores = Blueprint("chores", __name__, url_prefix="/chores")


@chores.route("/")
@min_clearance(ClearanceEnum.NORMAL)
def index():
    return render_template("chores/index.html")
