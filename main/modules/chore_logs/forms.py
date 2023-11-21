from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, DateField
from wtforms.validators import DataRequired


class ChoreLogDueDate(FlaskForm):
    due_date = DateField(format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Save")
