from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
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

class StartField(FlaskForm):
    client = StringField("Client", validators=[DataRequired()])
    project = StringField("Project", validators=[DataRequired()])
    submit = SubmitField("Start")

class NewForm(FlaskForm):
    new_client = StringField("New Client")
    new_project = StringField("New Project")
    submit = SubmitField("Submit")