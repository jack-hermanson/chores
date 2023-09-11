from sqlalchemy import func
from .models import List
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Length
from ..accounts.models import Account


list_name_length = Length(min=2, max=50)


class CreateEditList(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), list_name_length], render_kw={
        "autofocus": "true",
        "placeholder": "Boring things I have to do"
    }, description="What should this list be called?")
    accounts = SelectMultipleField(
        "Users",
        coerce=int,
        validators=[],
        description="Besides you, who should have access to this list?"
    )
    submit = SubmitField()


