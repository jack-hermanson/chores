from flask import Blueprint, redirect, url_for, flash, request, render_template
from .forms import CreateEditList
from ..accounts.models import Account
from flask_login import current_user, login_required
from .models import List
from main import db
from ..accounts.ClearanceEnum import ClearanceEnum
from ...utils.min_clearance import min_clearance

lists = Blueprint("lists", __name__, url_prefix="/lists")


def get_user_options():
    options = Account.query\
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
        new_list.title = form.title.data
        new_list.description = "Auto generated!"

        accounts = []
        for account_id in form.accounts.data:
            accounts.append(Account.query.filter(Account.account_id == account_id).first())
        new_list.accounts = accounts

        db.session.add(new_list)
        db.session.commit()
        flash(f"List \"{new_list.title}\" created successfully.", "success")
        return redirect(url_for("lists.index"))

    return render_template("lists/create-edit.html",
                           mode="Create",
                           form=form)


@lists.route("/edit/<int:list_id>")
@min_clearance
def edit(list_id: int):
    pass




