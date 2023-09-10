from sqlalchemy import func
from .models import Account
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, BooleanField, EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email


class Login(FlaskForm):
    name = StringField("Name", validators=[DataRequired()], render_kw={
        "autofocus": "true",
        "placeholder": "jack"
    })
    password = PasswordField("Password", validators=[DataRequired()], render_kw={
        "placeholder": "passw0rd!"
    })
    remember = BooleanField("Remember Me", default=False)
    submit = SubmitField("Log In")


class Create(FlaskForm):
    name = StringField("Name", validators=[DataRequired()], render_kw={
        "autofocus": "true"
    })
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", "Your passwords must match.")
        ]
    )
    submit = SubmitField("Create Account")

    @staticmethod
    def validate_name(_, name):
        if Account.query.filter(func.lower(Account.name) == func.lower(name.data)).all():
            raise ValidationError("That name has already been taken.")

    @staticmethod
    def validate_email(_, email):
        if Account.query.filter(func.lower(Account.email) == func.lower(email.data)).all():
            raise ValidationError("That email has already been taken.")
