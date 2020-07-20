from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import (DataRequired, Length, Email, EqualTo, ValidationError)

class LoginForm(FlaskForm):
    user_name = StringField("Username", validators=[DataRequired(), Length(max=40)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    tzs = [
        ("US/Eastern", "US/Eastern"),
        ("US/Central", "US/Central"),
        ("US/Pacific", "US/Pacific")
        ]
    user_name = StringField("Username", validators=[DataRequired(), Length(max=40)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    timezone = SelectField("Local Timezone", choices=tzs, validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                    validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField("Register")

class StartForm(FlaskForm):
    project = StringField("Project", validators=[DataRequired()])
    task = StringField("Task", validators=[DataRequired()])
    note = StringField("Note", validators=[DataRequired()])
    
    submit = SubmitField("Start")

class DateSelectForm(FlaskForm):
    range_begin = DateField("Starting Date")
    range_end = DateField("Ending Date")
    submit = SubmitField("Submit")

class ItemEditForm(FlaskForm):
    project = StringField("Project")
    task = StringField("Task")
    note = StringField("Note")
    start = StringField("Start Time")
    stop = StringField("Stop Time")
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    tzs = [
        ("US/Eastern", "US/Eastern"),
        ("US/Central", "US/Central"),
        ("US/Pacific", "US/Pacific")
        ]
    user_name = StringField("Username", validators=[DataRequired(), Length(max=40)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    timezone = SelectField("Local Timezone", choices=tzs, validators=[DataRequired()])
    update = SubmitField("Update")
