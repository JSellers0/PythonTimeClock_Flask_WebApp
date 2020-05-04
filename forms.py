from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import (DataRequired, Length, Email, EqualTo, ValidationError)

class LoginForm(FlaskForm):
    user_name = StringField("Username", validators=[DataRequired(), Length(max=40)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    user_name = StringField("Username", validators=[DataRequired(), Length(max=40)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                    validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField("Register")

class StartForm(FlaskForm):
    project = StringField("Project", validators=[DataRequired()])
    task = StringField("Task", validators=[DataRequired()])
    note = StringField("Note", validators=[DataRequired()])
    
    submit = SubmitField("Start")

class NewForm(FlaskForm):
    new_client = StringField("New Client")
    new_project = StringField("New Project")
    submit = SubmitField("Submit")

class AdjustTimeForm(FlaskForm):
    range_begin = DateField("Beginning Date")
    range_end = DateField("Ending Date")
    submit = SubmitField("Submit")