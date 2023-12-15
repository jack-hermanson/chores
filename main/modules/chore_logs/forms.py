from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, DateField, StringField, BooleanField
from wtforms.validators import DataRequired


class ChoreLogDueDate(FlaskForm):
    due_date = DateField(format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Save")


class SearchAndFilterForm(FlaskForm):
    search_text = StringField(label="Search")
    show_archived = BooleanField(label="Show Archived")
