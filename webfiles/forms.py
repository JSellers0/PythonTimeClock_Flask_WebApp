from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField
from wtforms.validators import DataRequired

class StartForm(FlaskForm):
    client_list = SelectField(u"Select a Client", validators=[DataRequired()])
    project_list = SelectField(u"Select a Project", validators=[DataRequired()])
    start = SubmitField("Start")

class NewForm(FlaskForm):
    new_client = StringField("client_name")
    new_project = StringField("client_name")
    submit = SubmitField("Submit")

    # Custom Validators to check if client or project already exist in the database