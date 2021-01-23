from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from myshit import s_mysql, s_host, s_ask

# ToDo: Make secret key , DB URI, API URI actually secret.

app = Flask(__name__)


app.secret_key = s_ask

db_uri = "mysql+pymysql://clock:" + s_mysql + "@" + s_host + "/clock"

app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt()
bcrypt.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'

aws_route = "http://192.168.0.203/api/clock"
