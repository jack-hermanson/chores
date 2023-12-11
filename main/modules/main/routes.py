from flask import Blueprint, redirect, url_for
from main import logger

main = Blueprint("main", __name__, url_prefix="")


@main.route("/")
def index():
    logger.debug("Redirecting home page to chore logs index")
    return redirect(url_for("chore_logs.index"))
    # return render_template("main/index.html")
