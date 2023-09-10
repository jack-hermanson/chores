from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_user, logout_user, current_user, login_required
from main import db, bcrypt
from .forms import Login, Create
from .models import Account
from datetime import datetime

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
def login(prefilled_form: Login or None = None):
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("main.index"))

    if prefilled_form is not None:
        return render_template(
            "accounts/login.html",
            form=prefilled_form
        )

    form = Login()
    if form.password.render_kw.get("autofocus") is not None:
        del form.password.render_kw["autofocus"]
    form.name.render_kw["autofocus"] = "true"

    if form.validate_on_submit():
        user = Account.query.filter(Account.name == form.name.data).first_or_404()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            last_login = user.last_login.strftime('%a %d %b %Y, %I:%M%p') \
                if user.last_login is not None else "never"
            flash(f"Welcome back, {user.name}. Your last login was {last_login}.", "info")
            current_user.last_login = datetime.now()
            db.session.commit()

            return redirect(next_page) if next_page else redirect(url_for("main.index"))
        else:
            flash("Bad login credentials. You should really use a password manager.", "danger")

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
        flash(f"Alright, {user.name}. Enter your password to log in.", 'success')

        prefilled_login_form = Login()
        prefilled_login_form.name.data = user.name
        prefilled_login_form.remember.data = True
        if prefilled_login_form.name.render_kw.get("autofocus") is not None:
            del prefilled_login_form.name.render_kw["autofocus"]
            prefilled_login_form.password.render_kw["autofocus"] = "true"
        return login(prefilled_login_form)
        # return redirect(url_for('accounts.login'))
    return render_template('accounts/register.html',
                           form=form)


@accounts.route("/logout", methods=["POST"])
def logout():
    name = current_user.name
    if not current_user.is_authenticated:
        flash("You are not logged in, so you cannot log out!", "danger")
        return redirect(url_for("accounts.login"))

    logout_user()
    flash(f"Okay, bye {name}.", "info")
    return redirect(url_for("main.index"))
