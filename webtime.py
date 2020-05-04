import requests
import pandas as pd

from dateutil import tz
from datetime import datetime as dt

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, login_required, current_user, logout_user, login_user

from flask_bcrypt import Bcrypt

from forms import *
from models import UserManager

from timeclock import TimeClock

# ToDo: TimeClock class to handle requests and data

app = Flask(__name__)
app.secret_key = b';aeirja_)(_9u-a9jdfae90ej-e09!@aldjfa;'

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "danger"
login_manager.init_app(app)

bcrypt = Bcrypt(app)

user_manager = UserManager()

timeclock = TimeClock()

@login_manager.user_loader
def load_user(userid):
    return user_manager.get_user(userid)

@app.route("/webtime", methods=["GET", "PUT"])
def webtime():
    # ToDo: AJAX / JS for stop button.  Remove app.route("/stop")
    message = "Click Start to start timing!"
    if timeclock.stop:
        message = "Stopped tracking {pname} - {tname} \n {nname}".format(
            pname=timeclock.project.get("name"),
            tname=timeclock.task.get("name"),
            nname=timeclock.note.get("name")
        )
        timeclock.reset_timelog_fields()
    elif timeclock.timelogid != 0:
        message = "Started {pname} - {tname} \n{nname} at {start}".format(
            pname=timeclock.project.get("name"),
            tname=timeclock.task.get("name"),
            nname=timeclock.note.get("name"),
            start=(
                dt.strptime(timeclock.start, "%Y-%m-%dT%H:%M:%SZ")
                .replace(tzinfo=tz.tzutc())
                .astimezone(tz.tzlocal())
                .strftime("%Y-%m-%d %H:%M")
                )
        )
    return render_template("webtime.html", title="PythonTimeClock", message=message)

@app.route("/webtime/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("webtime"))
    form = RegisterForm()
    if form.validate_on_submit():
        if timeclock.register_user(form):
            return redirect(url_for("login"))
    return render_template("register.html", title="Registration", form=form)

@app.route("/webtime/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users"))
    form = LoginForm()
    if form.validate_on_submit():
        cur_user = timeclock.login_user(form)
        if cur_user:
            user_manager.add_user(cur_user.get_id(), cur_user)
            login_user(cur_user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("webtime"))

    return render_template("login.html", title="Login", form=form)

@app.route("/webtime/start", methods=["POST", "GET"])
@login_required
def start():
    # Get lists for Start page
    project_list, task_list, note_list = timeclock.get_start_lists()

    form = StartForm()
    if form.validate_on_submit():
        if timeclock.start_timing(form):
            return redirect(url_for("webtime"))
    return render_template("start.html", form=form, projects=project_list, tasks=task_list, notes=note_list)

@app.route("/webtime/stop", methods=["GET", "PUT"])
@login_required
def stop():
    if not timeclock.stop_timing():
        flash("There was an error stopping the timeclock", "danger")
        return redirect(url_for("webtime"))
    # ToDo: Look up how to pass message to url_for
    return redirect(url_for("webtime"))

# ToDo: Extensively test new creation process and then delete this shit.
@app.route("/webtime/new", methods=["POST", "GET"])
@login_required
def new():
    form = NewForm()
    if form.validate_on_submit():
        if form.new_task.data:
            resp = requests.post(aws_route+"/tasks", json={"task_name": form.new_task.data})
            if resp == 201:
                task_success = True
            else:
                task_success = False
        else:
            no_task = True
        if form.new_project.data:
            resp = requests.post(aws_route+"/projects", json={"project_name": form.new_project.data})
            if resp == 201:
                project_success = True
            else:
                project_success = False
        else:
            no_project = True
        if (task_success or no_task) and (project_success or no_project):
            flash("New items successfully added!", "success")
            return redirect(url_for("start"))
        elif not task_success:
            flash("The task name you submitted already exists")
        elif not project_success:
            flash("The project name you submitted alread exists.")
    return render_template("new.html", form=form)

@app.route("/webtime/adjust")
#@login_required
def adjust():
    return render_template("adjust.html")

@app.route("/webtime/adjust/time", methods=["GET", "POST"])
#@login_required
def adjust_time():
    form = AdjustTimeForm()
    init = True
    rows=None
    if form.validate_on_submit():
        # summary_data = timeclock.get_daterange_rows(form)
        init = False
    return render_template("adjust_time.html", form=form, init=init, data=summary_data)

@app.route("/webtime/adjust/task")
#@login_required
def adjust_task():
    return render_template("adjust_task.html")

@app.route("/webtime/adjust/project")
#@login_required
def adjust_project():
    return render_template("adjust_project.html")

@app.route("/webtime/adjust/note")
#@login_required
def adjust_note():
    return render_template("adjust_note.html")

@app.route("/webtime/report")
#@login_required
def report():
    return render_template("report.html")

@app.route("/users")
#@login_required
def users():
    return render_template("users.html")

@app.route("/webtime/logout")
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("webtime"))

if __name__ == "__main__":
    app.run(debug=True)