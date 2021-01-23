from config import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(userid=userid).first()

class User(db.Model, UserMixin):
    userid = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_token = db.Column(db.String(150), unique=True, nullable=False)
    timezone = db.Column(db.String(100), nullable=False, default="US/Eastern")

    def __init__(self, user_name, email, user_token, timezone):
        self.user_name = user_name
        self.email = email
        self.user_token = user_token
        self.timezone = timezone

    def __repr__(self):
        return "User({}, {})".format(self.user_name, self.email)

    def get_id(self):
        return str(self.userid)
