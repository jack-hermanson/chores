from sqlalchemy import func
from .models import Account
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, BooleanField, EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Length

name_length = Length(min=2, max=15)
password_length = Length(max=100)


class Login(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), name_length], render_kw={
        "autofocus": "true",
        "placeholder": "jack"
    })
    password = PasswordField("Password", validators=[DataRequired(), password_length], render_kw={
        "placeholder": "passw0rd!"
    })
    remember = BooleanField("Remember Me", default=True)
    submit = SubmitField("Log In")

    @staticmethod
    def validate_name(_, name):
        if not Account.query.filter(func.lower(Account.name) == func.lower(name.data)).count():
            raise ValidationError("Doesn't exist.")


class CreateOrEditFormBase(FlaskForm):
    """Just the base - inherit this in create and edit"""
    name = StringField(
        "Name",
        validators=[DataRequired(), name_length],
        render_kw={
            "autofocus": "true",
            "placeholder": "jack"
        },
        description="Just your first name, not case-sensitive."
    )
    capitalize_name = BooleanField(
        "Capitalize Name",
        validators=[],
        default=False,
        description="This will capitalize your entire name. Check this if your name is initials.",
        false_values=('False', 'false', '')
    )
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()])

    @staticmethod
    def validate_email(_, email):
        if Account.query.filter(func.lower(Account.email) == func.lower(email.data)).all():
            raise ValidationError("That email has already been taken.")


class Edit(CreateOrEditFormBase):
    password = PasswordField("Password", validators=[password_length])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            EqualTo("password", "Your passwords must match.")
        ]
    )

    @staticmethod
    def validate_password(_, password):
        if len(password.data) > password_length.max:
            raise ValidationError(f"Name must be fewer than {password_length.max} characters")


class Create(CreateOrEditFormBase):
    password = PasswordField("Password", validators=[DataRequired(), password_length])
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
        if name.data.lower() == "test" or name.data.lower() == "admin":
            raise ValidationError("You can't use that one.")
