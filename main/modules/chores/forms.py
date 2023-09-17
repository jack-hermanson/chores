from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class CreateEditChore(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)], render_kw={"autofocus": "true"})
    description = TextAreaField("Description", validators=[Length(max=255)])
    submit = SubmitField()
