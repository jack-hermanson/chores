from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length, ValidationError, Optional

from main.modules.chores.RepeatTypeEnum import RepeatTypeEnum
from utils.date_time_enums import DayOfWeekEnum


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
            (int(RepeatTypeEnum.DAY_OF_THE_WEEK), "Day of the Week"),
            (int(RepeatTypeEnum.DAY_OF_MONTH), "Day of Month")
        ],
        default=int(RepeatTypeEnum.NONE)
    )
    repeat_days = IntegerField(
        "Repeats Every",
        description="This chore will repeat every (this amount) of days.")
    repeat_day_of_week = SelectField(
        "Day of Week",
        description="This chore will repeat on this day of the week.",
        choices=[
            (int(day_of_week), day_of_week.name.capitalize())
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
    repeat_day_of_month = SelectField(
        "Day of Month",
        description="This chore will repeat on this day of every month.",
        choices=[
            *[(x, x) for x in range(1, 29)],
            (31, "Last Day of Month")
        ],
        validators=[Optional()]
    )
    list = SelectField(
        "Chore List",
        description="Which list does this chore belong to?",
        choices=[],  # set in controller
        validators=[DataRequired()]
    )
    owner = SelectField(
        "Owner",
        description="Who is responsible for this chore?",
        choices=[],  # set in controller
        validators=[DataRequired()]
    )
    due_date = DateField(
        "Due Date",
        description="When is this one-time chore due?",
        validators=[],
        format="%Y-%m-%d"
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
            and (form.repeat_days.data < 1
                 or form.repeat_days.data > 365)
        ):
            raise ValidationError("Repeat Days must be between 1 and 365.")

    @staticmethod
    def validate_repeat_day_of_week(form, _):
        repeat_type = RepeatTypeEnum(int(form.repeat_type.data))

        if (
            repeat_type == RepeatTypeEnum.DAY_OF_THE_WEEK
            and form.repeat_day_of_week.data is not None
            and (int(form.repeat_day_of_week.data) > 6 or int(form.repeat_day_of_week.data) < 0)
        ):
            raise ValidationError("Repeat day of week must be between 0 and 6.")

    @staticmethod
    def validate_repeat_day_of_month(form, _):
        repeat_type = RepeatTypeEnum(int(form.repeat_type.data))

        if (
            repeat_type == RepeatTypeEnum.DAY_OF_MONTH
            and form.repeat_day_of_month.data is None
        ):
            raise ValidationError("Day of month is required.")

    @staticmethod
    def validate_due_date(form, _):
        repeat_type = RepeatTypeEnum(int(form.repeat_type.data))

        if (
            repeat_type == RepeatTypeEnum.NONE
            and form.due_date.data is None
        ):
            raise ValidationError("Due date is required for one-off chores.")
