from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
import logging

from main.modules.accounts.ClearanceEnum import ClearanceEnum
from main.modules.chores.forms import CreateEditChore
from main.utils.min_clearance import min_clearance
from flask_login import current_user
from .models import Chore
from main import db
from .RepeatTypeEnum import RepeatTypeEnum
from ...utils.DateTimeEnums import DayOfWeekEnum

chores = Blueprint("chores", __name__, url_prefix="/chores")


@chores.route("/")
@min_clearance(ClearanceEnum.NORMAL)
def index():
    chores_list = Chore.query.filter(Chore.owner == current_user).all()

    return render_template("chores/index.html",
                           chores_list=chores_list)


@chores.route("/create", methods=["GET", "POST"])
@min_clearance(ClearanceEnum.NORMAL)
def create():
    form = CreateEditChore()

    if form.validate_on_submit():
        new_chore = Chore()
        new_chore.title = form.title.data
        new_chore.description = form.description.data
        new_chore.owner = current_user
        new_chore.repeat_type = RepeatTypeEnum(int(form.repeat_type.data))
        if new_chore.repeat_type == RepeatTypeEnum.DAYS:
            new_chore.repeat_days = form.repeat_days.data
        elif new_chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            new_chore.repeat_day_of_week = DayOfWeekEnum(int(form.repeat_day_of_week.data))

        db.session.add(new_chore)
        db.session.commit()
        flash(f"Chore \"{new_chore.title}\" created successfully.", "success")
        return redirect(url_for("chores.index"))

    return render_template("chores/create-edit.html",
                           mode="Create",
                           form=form)


@chores.route("/edit/<int:chore_id>", methods=["GET", "POST"])
@min_clearance(ClearanceEnum.NORMAL)
def edit(chore_id: int):
    form = CreateEditChore()
    chore = Chore.query.filter(Chore.chore_id == chore_id).first_or_404()

    if form.validate_on_submit():
        chore.title = form.title.data
        chore.description = form.description.data
        chore.repeat_type = RepeatTypeEnum(int(form.repeat_type.data))

        if chore.repeat_type == RepeatTypeEnum.NONE:
            chore.repeat_days = None
            chore.repeat_day_of_week = None
        elif chore.repeat_type == RepeatTypeEnum.DAYS:
            chore.repeat_day_of_week = None
            chore.repeat_days = form.repeat_days.data
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            chore.repeat_days = None
            chore.repeat_day_of_week = DayOfWeekEnum(int(form.repeat_day_of_week.data))
        else:
            logging.error(f"Invalid repeat_type {chore.repeat_type}")
            return abort(400)

        db.session.commit()
        flash(f"Chore \"{chore.title}\" edited successfully.", "success")
        return redirect(url_for("chores.index"))
    elif request.method == "GET":
        form.title.data = chore.title
        form.description.data = chore.description
        form.repeat_type.data = str(int(chore.repeat_type))
        if chore.repeat_type == RepeatTypeEnum.DAYS:
            form.repeat_days.data = chore.repeat_days
        elif chore.repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
            form.repeat_day_of_week.data = str(int(chore.repeat_day_of_week))

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
        return ""
    if repeat_type == RepeatTypeEnum.DAYS:
        return render_template("chores/create-edit-partials/repeat-days.html",
                               form=form)
    if repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK:
        return render_template("chores/create-edit-partials/repeat-day-of-week.html",
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
