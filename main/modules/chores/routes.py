from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user

from main import db, logger
from main.modules.accounts.ClearanceEnum import ClearanceEnum
from main.modules.chores.forms import CreateEditChore
from utils.date_time_enums import DayOfWeekEnum
from utils.min_clearance import min_clearance
from .RepeatTypeEnum import RepeatTypeEnum
from .models import Chore
from ..accounts.models import Account
from ..lists.models import List
from ..lists.services import get_user_lists
from ..chore_logs.services import get_previous_logs

chores = Blueprint("chores", __name__, url_prefix="/chores")


@chores.route("/create", methods=["GET", "POST"])
@min_clearance(ClearanceEnum.NORMAL)
def create():
    form = CreateEditChore()
    form.list.choices = [(ls.list_id, ls.title) for ls in get_user_lists()]
    form.owner.data = str(current_user.account_id)
    form.owner.choices = [(current_user.account_id, current_user.name)]
    form.owner.render_kw = {"disabled": True}

    if form.validate_on_submit():
        new_chore = Chore()
        new_chore.title = form.title.data.strip()
        new_chore.description = form.description.data
        new_chore.owner = current_user
        new_chore.repeat_type = RepeatTypeEnum(int(form.repeat_type.data))
        if new_chore.repeat_type == RepeatTypeEnum.NONE:
            new_chore.one_time_due_date = form.due_date.data
        elif new_chore.repeat_type == RepeatTypeEnum.DAYS:
            new_chore.repeat_days = form.repeat_days.data
        elif new_chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            new_chore.repeat_day_of_week = DayOfWeekEnum(int(form.repeat_day_of_week.data))
        elif new_chore.repeat_type == RepeatTypeEnum.DAY_OF_MONTH:
            new_chore.repeat_day_of_month = int(form.repeat_day_of_month.data)

        associated_list = List.query.get_or_404(form.list.data)
        new_chore.list = associated_list

        db.session.add(new_chore)
        db.session.commit()
        flash(f"Chore \"{new_chore.title}\" created successfully.", "success")
        return redirect(url_for("chore_logs.index"))

    return render_template("chores/create-edit.html",
                           mode="Create",
                           form=form)


@chores.route("/edit/<int:chore_id>", methods=["GET", "POST"])
@min_clearance(ClearanceEnum.NORMAL)
def edit(chore_id: int):
    form = CreateEditChore()
    form.list.choices = [(ls.list_id, ls.title) for ls in get_user_lists()]
    chore = Chore.query.filter(Chore.chore_id == chore_id).first_or_404()
    # todo - what if the list changes? need to make this an htmx thing
    form.owner.choices = [(a.account_id, a.name) for a in chore.list.accounts]
    form.due_date.data = chore.one_time_due_date

    if form.validate_on_submit():
        chore.title = form.title.data.strip()
        chore.description = form.description.data
        chore.repeat_type = RepeatTypeEnum(int(form.repeat_type.data))
        chore.owner = Account.query.filter(Account.account_id == int(form.owner.data)).first_or_404()

        if chore.repeat_type == RepeatTypeEnum.NONE:
            chore.repeat_days = None
            chore.repeat_day_of_week = None
            chore.repeat_day_of_month = None
            chore.one_time_due_date = form.due_date.data
            chore.chore_logs.clear()
        elif chore.repeat_type == RepeatTypeEnum.DAYS:
            chore.repeat_days = form.repeat_days.data
            chore.repeat_day_of_week = None
            chore.repeat_day_of_month = None
            chore.one_time_due_date = None
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            chore.repeat_days = None
            chore.repeat_day_of_week = DayOfWeekEnum(int(form.repeat_day_of_week.data))
            chore.repeat_day_of_month = None
            chore.one_time_due_date = None
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_MONTH:
            chore.repeat_days = None
            chore.repeat_day_of_week = None
            chore.repeat_day_of_month = int(form.repeat_day_of_month.data)
            chore.one_time_due_date = None
        else:
            logger.error(f"Invalid repeat_type {chore.repeat_type}")
            return abort(400)

        associated_list = List.query.get_or_404(form.list.data)
        chore.list = associated_list
        chore.notifications_enabled = form.notifications_enabled.data

        db.session.commit()
        flash(f"Chore \"{chore.title}\" edited successfully.", "success")
        return redirect(url_for("chore_logs.index"))
    elif request.method == "GET":
        form.title.data = chore.title
        form.description.data = chore.description
        form.repeat_type.data = str(int(chore.repeat_type))
        if chore.repeat_type == RepeatTypeEnum.DAYS:
            form.repeat_days.data = chore.repeat_days
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            form.repeat_day_of_week.data = str(int(chore.repeat_day_of_week))
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_MONTH:
            form.repeat_day_of_month.data = str(int(chore.repeat_day_of_month))
        form.list.data = str(chore.list.list_id)
        form.owner.data = str(chore.owner.account_id)
        form.notifications_enabled.data = chore.notifications_enabled
        logger.info(f"form.list.data {form.list.data}")

    return render_template("chores/create-edit.html",
                           mode="Edit",
                           chore_id=chore_id,
                           form=form)


@chores.route("/repeat-type")
@min_clearance(ClearanceEnum.NORMAL)
def get_repeat_type():

    repeat_type = RepeatTypeEnum(int(request.args.get('repeat_type')))
    form = CreateEditChore()

    if repeat_type == RepeatTypeEnum.NONE:
        return render_template("chores/create-edit-partials/due-date.html",
                               form=form)
    if repeat_type == RepeatTypeEnum.DAYS:
        return render_template("chores/create-edit-partials/repeat-days.html",
                               form=form)
    if repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
        return render_template("chores/create-edit-partials/repeat-day-of-week.html",
                               form=form)
    if repeat_type == RepeatTypeEnum.DAY_OF_MONTH:
        return render_template("chores/create-edit-partials/repeat-day-of-month.html",
                               form=form)


@chores.route("/delete/<int:chore_id>", methods=["DELETE"])
@min_clearance(ClearanceEnum.NORMAL)
def delete(chore_id):

    chore_to_delete = Chore.query.filter(Chore.chore_id == chore_id).first_or_404()
    db.session.delete(chore_to_delete)
    db.session.commit()

    chores_list = Chore.query.all()

    return render_template("chores/index-partials-chores.html",
                           chores_list=chores_list)


@chores.route("/<int:chore_id>")
@min_clearance(ClearanceEnum.NORMAL)
def details(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    previous_logs = get_previous_logs(chore_id)
    return render_template("chores/details.html",
                           chore=chore,
                           previous_logs=previous_logs)
