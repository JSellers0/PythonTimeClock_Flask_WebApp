from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = b';aeirja_)(_9u-a9jdfae90ej-e09!@aldjfa;'

db_uri = "mysql://clock:" + "M4xG3*@jgOIRdEgmjUfSV" + "@localhost/clock"

app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt()
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'danger'

aws_route = "http://192.168.0.202/api/clock"
