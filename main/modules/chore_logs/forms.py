from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired


class ChoreLogDueDate(FlaskForm):
    due_date = DateTimeLocalField(format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField("Save")
