from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional

from main.modules.chores.RepeatTypeEnum import RepeatTypeEnum
from main.utils.DateTimeEnums import DayOfWeekEnum


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
    repeat_days = IntegerField(
        "Repeats Every",
        description="This chore will repeat every (this amount) of days.")
    repeat_day_of_week = SelectField(
        "Day of Week",
        description="This chore will repeat on this day of the week.",
        choices=[
            (int(day_of_week), str(day_of_week).replace("DayOfWeekEnum.", "").capitalize())
            for day_of_week in [
                DayOfWeekEnum.MONDAY,
                DayOfWeekEnum.TUESDAY,
                DayOfWeekEnum.WEDNESDAY,
                DayOfWeekEnum.THURSDAY,
                DayOfWeekEnum.FRIDAY,
                DayOfWeekEnum.SATURDAY,
                DayOfWeekEnum.SUNDAY
            ]
        ],
        validators=[Optional()]

    )
    submit = SubmitField()

    @staticmethod
    def validate_repeat_days(form, _):
        repeat_type = RepeatTypeEnum(int(form.repeat_type.data))

        if repeat_type == RepeatTypeEnum.DAYS and form.repeat_days.data is None:
            raise ValidationError("Repeat days is required.")

        if (
                repeat_type == RepeatTypeEnum.DAYS
                and form.repeat_days.data is not None
                and (
                form.repeat_days.data < 1
                or form.repeat_days.data > 365)
        ):
            raise ValidationError("Repeat Days must be between 1 and 365.")

    @staticmethod
    def validate_repeat_day_of_week(form, _):
        repeat_type = RepeatTypeEnum(int(form.repeat_type.data))

        if (
            repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK
            and form.repeat_day_of_week.data is not None
            and (
                int(form.repeat_day_of_week.data) > 6 or int(form.repeat_day_of_week.data) < 0
            )
        ):
            raise ValidationError("Repeat day of week must be between 0 and 6.")
