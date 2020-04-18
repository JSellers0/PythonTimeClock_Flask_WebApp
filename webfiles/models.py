from datetime import datetime
from flask_sqlalchemy import SQLAlchemy, Model

db = SQLAlchemy()

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(String(120), uniuqe=True, nullable=False)
    password = db.Column(String(60), nullable=False)

    def __repr__(self):
        return "User({}, {})".format(self.username, self.email)

class Client(db.Model):
    clientid = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return "Client({}, {})".format(self.clientid, self.client_name)

class Project(db.Model):
    projectid = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return "project({}, {})".format(self.projectid, self.project_name)

class Timelog(db.Model):
    timelogid = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    stop = db.Column(db.DateTime)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)
    clientid = db.Column(db.Integer, db.ForeignKey("client.clientid"), nullable=False)
    projectid = db.Column(db.Integer, db.ForeignKey("project.projectid"), nullable=False)

class User_Client_Exclusion(db.Model):
    clientexclusionid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)
    clientid = db.Column(db.Integer, db.ForeignKey("client.clientid"), nullable=False)

class User_Project_Exclusion(db.Model):
    projectexclusionid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)
    projectid = db.Column(db.Integer, db.ForeignKey("project.projectid"), nullable=False)
