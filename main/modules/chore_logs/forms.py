from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, DateField, DateTimeField, DateTimeLocalField, StringField, BooleanField, FieldList, SearchField, SelectMultipleField
from wtforms.validators import DataRequired


class ChoreLogDueDate(FlaskForm):
    due_date = DateField(format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Save")


class ChoreLogCompletedDate(FlaskForm):
    completed_date = DateTimeLocalField(format='%Y-%m-%dT%H:%M', validators=[])
    submit = SubmitField("Save")


class SearchAndFilterForm(FlaskForm):
    search_text = SearchField(label="Search")
    show_archived = BooleanField(label="Show Archived")
    lists = SelectMultipleField(label="Filter Lists")  # set choices in controller
