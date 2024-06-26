from flask import Blueprint, redirect, url_for, flash, request, render_template, abort
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
@min_clearance(ClearanceEnum.NORMAL)
def index():
    lists_list = List.query.filter(List.accounts.contains(current_user)).all()
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
        new_list.owner = current_user
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
    list = db.session.query(List).filter(List.list_id == list_id).first_or_404()
    # todo there is no check for ownership before deleting
    db.session.delete(list)
    db.session.commit()
    lists_list = List.query.all()
    return render_template("lists/index-partial-lists.html",
                           lists_list=lists_list)


# Return HTMX for when you click the trash button
@lists.route("/remove-user-from-list", methods=["PUT"])
@min_clearance(ClearanceEnum.NORMAL)
def remove_user_from_list():
    list_id = int(request.args.get("list_id"))
    account_id = int(request.args.get("account_id"))

    list_in_question = List.query.filter(List.list_id == list_id).first_or_404()
    account = Account.query.filter(Account.account_id == account_id).first_or_404()

    list_in_question.accounts = list(filter(lambda a: a.account_id != account.account_id, list_in_question.accounts))
    db.session.commit()

    return render_template("lists/list-partial.html",
                           list=list_in_question)


@lists.route("/remove-self-from-list/<int:list_id>")
@min_clearance(ClearanceEnum.NORMAL)
def remove_self_from_list(list_id: int):
    list_in_question = List.query.filter(List.list_id == list_id).first_or_404()
    if list_in_question.owner == current_user:
        return abort(400)
    if not list_in_question.accounts.__contains__(current_user):
        return abort(403)

    list_in_question.accounts = list(filter(lambda a: a.account_id != current_user.account_id, list_in_question.accounts))
    db.session.commit()
    flash("Removed self from list successfully.", "success")

    return redirect(url_for("lists.index"))
