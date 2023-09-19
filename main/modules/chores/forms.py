from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

from main.modules.chores.RepeatTypeEnum import RepeatTypeEnum


class CreateEditChore(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)], render_kw={"autofocus": "true"})
    description = TextAreaField("Description", validators=[Length(max=255)])
    repeat_type = SelectField(
        "Repeat Type",
        validators=[DataRequired()],
        description="How should this chore's frequency be measured?",
        choices=[
            (int(RepeatTypeEnum.NONE), "None"),
            (int(RepeatTypeEnum.DAYS), "Days"),
            (int(RepeatTypeEnum.DAY_OF_THE_WEEK), "Day of Week")
        ],
        default=RepeatTypeEnum.NONE
    )
    repeat_days = IntegerField("Repeats Every")
    submit = SubmitField()

    @staticmethod
    def validate_repeat_days(form, _):
        repeat_type = RepeatTypeEnum(int(form.repeat_type.data))

        if (
            repeat_type == RepeatTypeEnum.DAYS
            and form.repeat_days.data is not None
            and (
                form.repeat_days.data < 1
                or form.repeat_days.data > 365
            )
        ):
            raise ValidationError("Repeat Days must be between 1 and 365.")
