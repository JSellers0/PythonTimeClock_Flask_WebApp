import requests

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, login_required, current_user, logout_user, login_user

from flask_bcrypt import Bcrypt

from forms import LoginForm, RegisterForm
from models import MyUser

app = Flask(__name__)
app.secret_key = b';aeirja_)(_9u-a9jdfae90ej-e09!@aldjfa;'

aws_route = "http://ec2-35-175-208-202.compute-1.amazonaws.com/api"

login_manager = LoginManager()
login_manager.login_view = "app.login"
login_manager.login_message_category = "danger"
login_manager.init_app(app)

cur_user = MyUser()

bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(userid):
    return cur_user

@app.route("/webtime", methods=["GET", "PUT"])
def webtime():
    return render_template("webtime.html", title="PythonTimeClock")

@app.route("/webtime/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("webtime"))
    form = RegisterForm()
    if form.validate_on_submit():
        user = {
            "user_name": form.user_name.data,
            "email" : form.email.data,
            "encoded_password": bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        }
        resp = requests.post(aws_route+"/users", json=user)
        if resp.status_code == 201:
            flash("Account created for {}!  Please Log In.", "success")
            return redirect(url_for("login"))
    return render_template("register.html", title="Registration", form=form)

@app.route("/webtime/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users"))
    form = LoginForm()
    if form.validate_on_submit():
        user = {
            "user_name": form.user_name.data,
            "password" : form.password.data
            }
        response = requests.post(aws_route + "/users/name", json=user)
        if response.status_code == 200:
            cur_user = MyUser(response.json())
            login_user(cur_user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("webtime"))
        else:
            flash("User Not Recognized.  Please check your info or Register an Account!", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/users")
def users():
    return render_template("users.html")

@login_required
@app.route("/webtime/start", methods=["POST", "GET"])
def start():
    return render_template("start.html")

@login_required
@app.route("/webtime/new", methods=["POST", "GET"])
def new():
    return render_template("new.html")

@login_required
@app.route("/webtime/adjust")
def adjust():
    return render_template("adjust.html")

@login_required
@app.route("/webtime/adjust/time")
def adjust_time():
    return render_template("adjust_time.html")

@login_required
@app.route("/webtime/adjust/client")
def adjust_client():
    return render_template("adjust_client.html")

@login_required
@app.route("/webtime/adjust/project")
def adjust_project():
    return render_template("adjust_project.html")

@login_required
@app.route("/webtime/report")
def report():
    return render_template("report.html")

@app.route("/webtime/logout")
def logout():
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("webtime"))

if __name__ == "__main__":
    app.run(debug=True)