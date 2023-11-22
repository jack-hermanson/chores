from flask import Blueprint, redirect, url_for, flash, request, render_template
from .forms import CreateEditList
from ..accounts.models import Account
from flask_login import current_user, login_required
from .models import List
from main import db
from ..accounts.ClearanceEnum import ClearanceEnum
from utils.min_clearance import min_clearance
from . import services

lists = Blueprint("lists", __name__, url_prefix="/lists")


def get_user_options():
    options = Account.query \
        .filter(Account.account_id != current_user.account_id) \
        .order_by("name").all()
    return [(option.account_id, option.name) for option in options]


@lists.route("/")
@login_required
def index():
    lists_list = List.query.all()
    return render_template("lists/index.html",
                           lists_list=lists_list)


@lists.route("/create", methods=["GET", "POST"])
@min_clearance(ClearanceEnum.NORMAL)
# @login_required
def create():
    form = CreateEditList()
    form.accounts.choices = get_user_options()

    if form.validate_on_submit():
        new_list = List()
        services.set_list_values(new_list, form)

        db.session.add(new_list)
        db.session.commit()
        flash(f"List \"{new_list.title}\" created successfully.", "success")
        return redirect(url_for("lists.index"))

    return render_template("lists/create-edit.html",
                           mode="Create",
                           form=form)


@lists.route("/edit/<int:list_id>", methods=["GET", "POST"])
@min_clearance(ClearanceEnum.NORMAL)
def edit(list_id: int):
    matching_list = List.query.filter(List.list_id == list_id).first_or_404()
    form = CreateEditList()
    form.accounts.choices = get_user_options()

    if form.validate_on_submit():
        services.set_list_values(matching_list, form)

        db.session.commit()
        flash(f"List \"{matching_list.title}\" edited successfully.", "success")
        return redirect(url_for("lists.index"))
    elif request.method == "GET":
        form.accounts.data = [m.account_id for m in matching_list.accounts]
        form.title.data = matching_list.title
        form.description.data = matching_list.description

    return render_template("lists/create-edit.html",
                           mode="Edit",
                           form=form)


@lists.route("/delete/<int:list_id>", methods=["DELETE"])
@min_clearance(ClearanceEnum.NORMAL)
def delete(list_id: int):
    list = db.session.query(List).filter(List.list_id == list_id).first()
    db.session.delete(list)
    db.session.commit()
    lists_list = List.query.all()
    return render_template("lists/index-partial-lists.html",
                           lists_list=lists_list)
