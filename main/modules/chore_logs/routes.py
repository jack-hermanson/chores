from datetime import datetime

from flask import Blueprint, render_template, request, abort, Response, url_for, flash
from flask_login import current_user
from sqlalchemy import and_

from main import db
from main.modules.accounts.ClearanceEnum import ClearanceEnum
from utils.date_functions import extract_datetime
from utils.min_clearance import min_clearance
from . import services
from .forms import ChoreLogDueDate, SearchAndFilterForm, ChoreLogCompletedDate
from .models import ChoreLog
from ..chores.RepeatTypeEnum import RepeatTypeEnum
from ..lists.models import List

chore_logs = Blueprint("chore_logs", __name__, url_prefix="/chore-logs")


@chore_logs.route("/generate-all")
@min_clearance(ClearanceEnum.NORMAL)
def generate_all():
    chores = services.generate_next_chore_logs()
    return [chore.__str__() for chore in chores], 201


@chore_logs.route("/")
@min_clearance(ClearanceEnum.NORMAL)
def index():
    form = SearchAndFilterForm(request.args, meta={'csrf': False})
    populate_form_lists(form)

    chore_logs_list = services.generate_next_chore_logs(search_text=form.search_text.data or "",
                                                        show_archived=form.show_archived.data or False,
                                                        list_ids=[int(li) for li in form.lists.data])
    return render_template("chore_logs/index.html",
                           chore_logs_list=chore_logs_list,
                           form=form,
                           show_form=(form.show_form.data.lower() == "true"))


@chore_logs.route("/filtering")
@min_clearance(ClearanceEnum.NORMAL)
def filtering():
    form = SearchAndFilterForm(request.args, meta={'csrf': False})
    show_form = str(form.show_form.data).lower() == "true"
    # flip it
    show_form = not show_form
    form.show_form.data = show_form

    populate_form_lists(form)

    return render_template("chore_logs/chore-log-filtering-partial.html",
                           form=form,
                           show_form=show_form)


@chore_logs.route("/complete", methods=["POST"])
def complete():
    # auth stuff is taken care of here rather than decorator
    # so htmx doesn't replace partial with login page
    if not current_user.is_authenticated:
        flash("Sorry, your login must've expired. Please log in and try again.", "danger")
        resp = Response("OH WOW that's kinda weird you aren't logged in")
        resp.headers['hx-redirect'] = url_for("accounts.login")
        return resp, 401
    if not current_user.clearance >= ClearanceEnum.NORMAL:
        return abort(403)
    chore_log_id = int(request.args.get("chore_log_id"))
    stay_on_schedule = bool(request.args.get("stay_on_schedule"))
    updated_chore_log = services.complete(chore_log_id, stay_on_schedule)

    return render_template("chore_logs/chore-log-partial.html",
                           chore_log=updated_chore_log)


@chore_logs.route("/undo/<int:chore_log_id>", methods=["POST"])
@min_clearance(ClearanceEnum.NORMAL)
def undo(chore_log_id: int):
    replace_chore_log = services.undo_completion(chore_log_id)
    return render_template("chore_logs/chore-log-partial.html",
                           chore_log=replace_chore_log)


@chore_logs.route("/due-date", methods=["GET", "POST"])
def due_date():
    chore_log_id = request.args.get("chore_log_id")
    form = ChoreLogDueDate()

    if form.validate_on_submit():
        chore_log = ChoreLog.query.get_or_404(chore_log_id)
        chore_log.due_date = form.due_date.data
        db.session.commit()

        return render_template("chore_logs/chore-log-partial.html",
                               chore_log=chore_log)
    elif request.method == "GET":
        chore_log = ChoreLog.query.get_or_404(chore_log_id)
        form.due_date.data = chore_log.due_date.date()
        # form.due_date.data = chore_log.due_date.replace(second=0, microsecond=0)
        return render_template("chore_logs/chore-log-due-date-input-partial.html",
                               chore_log=chore_log,
                               chore_log_id=chore_log_id,
                               form=form)
    else:
        return f"BAD {form.errors}"


@chore_logs.route("/completed-date", methods=["GET", "POST"])
def completed_date():
    chore_log_id = request.args.get("chore_log_id")
    form = ChoreLogCompletedDate()
    if form.validate_on_submit():
        chore_log = ChoreLog.query.get_or_404(chore_log_id)
        new_completed_date = datetime.strptime(request.form.get("completed_date"), "%Y-%m-%dT%H:%M")

        try:
            # validation
            if new_completed_date > extract_datetime(datetime.now()):
                raise ValueError("Cannot be in the future")
            if chore_log.chore.repeat_type == RepeatTypeEnum.NONE:
                chore_logs_completed_since_then = []
            else:
                chore_logs_completed_since_then = ChoreLog.query.filter(and_(
                    ChoreLog.chore_id == chore_log.chore_id,  # same chore
                    ChoreLog.chore_log_id != chore_log.previous.chore_log_id,  # different chore log
                    ChoreLog.completed_date >= new_completed_date  # different chore log has date after this
                )).all()
            if len(chore_logs_completed_since_then) != 0:
                raise ValueError(f"There have been {len(chore_logs_completed_since_then)} completed chore logs since then {[f'{x.chore_log_id} {x.chore.title} {x.completed_date}' for x in chore_logs_completed_since_then]}")
        except Exception as e:
            return e.__str__()

        if chore_log.chore.repeat_type == RepeatTypeEnum.NONE:
            chore_log.completed_date = new_completed_date
        else:
            chore_log.previous.completed_date = new_completed_date
        db.session.commit()

        return render_template("chore_logs/chore-log-partial.html",
                               chore_log=chore_log)
    elif request.method == "GET":
        chore_log = ChoreLog.query.get_or_404(chore_log_id)
        form.completed_date.data = chore_log.previous.completed_date if chore_log.chore.repeat_type != RepeatTypeEnum.NONE else chore_log.completed_date
        if chore_log.previous and chore_log.previous.previous:
            min_date = chore_log.previous.previous.completed_date.strftime("%Y-%m-%dT%H:%M")
        else:
            min_date = None
        return render_template("chore_logs/chore-log-completed-date-input-partial.html",
                               chore_log=chore_log,
                               chore_log_id=chore_log_id,
                               form=form,
                               min_date=min_date,
                               max_date=datetime.now().strftime("%Y-%m-%dT%H:%M"))
    else:
        return f"BAD {form.errors}"


@chore_logs.route("/previous-logs/<int:chore_id>")
def get_previous_logs(chore_id):
    prev_logs = services.get_previous_logs(chore_id)
    return [str(log) for log in prev_logs]


# This is a helper function
def populate_form_lists(form):
    lists = List.query.filter(List.accounts.contains(current_user)).all()
    form.lists.choices = [(li.list_id, li.title) for li in lists]

    if len(form.lists.data) == 0:
        form.lists.data = [str(li.list_id) for li in lists]
