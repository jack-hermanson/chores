from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.fields import (SubmitField, DateField, DateTimeLocalField, BooleanField, SearchField, SelectMultipleField,
                            HiddenField)
from wtforms.validators import DataRequired


class ChoreLogDueDate(FlaskForm):
    due_date = DateField(format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Save")


class ChoreLogCompletedDate(FlaskForm):
    completed_date = DateTimeLocalField(format='%Y-%m-%dT%H:%M', validators=[])
    completed_by = SelectField("Completed By", choices=[], validators=[DataRequired()])
    submit = SubmitField("Save")


class SearchAndFilterForm(FlaskForm):
    search_text = SearchField(label="Search")
    show_archived = BooleanField(label="Show Archived")
    lists = SelectMultipleField(label="Filter Lists")  # set choices in controller
    show_form = HiddenField(default="false")
