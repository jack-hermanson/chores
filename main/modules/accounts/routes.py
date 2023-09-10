from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_user, logout_user, current_user, login_required
from main import db, bcrypt
from .forms import Login, Create
from .models import Account

accounts = Blueprint("accounts", __name__, url_prefix="/accounts")


@accounts.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("accounts.login"))
    else:
        return redirect(url_for("accounts.profile"))


@accounts.route("/me")
@login_required
def profile():
    return render_template("accounts/me.html")


@accounts.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.index"))

    form = Login()

    if form.validate_on_submit():
        user = Account.query.filter(Account.name == form.name.data).first_or_404()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            flash("Logged in successfully.", "info")
            return redirect(next_page) if next_page else redirect(url_for("main.index"))

    return render_template(
        "accounts/login.html",
        form=form
    )


@accounts.route("/register", methods=["GET", "POST"])
def register():
    form = Create()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Account()
        user.name = form.name.data.lower()
        user.password = hashed_password
        user.email = form.email.data.lower()
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully.', 'success')
        return redirect(url_for('accounts.login'))
    return render_template('accounts/register.html',
                           form=form)


@accounts.route("/logout")
def logout():
    if not current_user.is_authenticated:
        flash("You are not logged in, so you cannot log out!", "danger")
        return redirect(url_for("accounts.login"))

    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main.index"))
