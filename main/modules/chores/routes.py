from flask import Blueprint, render_template, flash, redirect, url_for

from main.modules.accounts.ClearanceEnum import ClearanceEnum
from main.modules.chores.forms import CreateEditChore
from main.utils.min_clearance import min_clearance
from flask_login import current_user
from .models import Chore
from main import db

chores = Blueprint("chores", __name__, url_prefix="/chores")


@chores.route("/")
@min_clearance(ClearanceEnum.NORMAL)
def index():
    chores_list = Chore.query.all()
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

        db.session.add(new_chore)
        db.session.commit()
        flash(f"Chore \"{new_chore.title}\" created successfully.", "success")
        return redirect(url_for("chores.index"))

    return render_template("chores/create-edit.html",
                           mode="Create",
                           form=form)

