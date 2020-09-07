from dateutil import tz
from datetime import datetime as dt

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, login_required, current_user, logout_user, login_user

from flask_bcrypt import Bcrypt

from forms import *
from models import UserManager

from timeclock import TimeClock

app = Flask(__name__)
app.secret_key = b';aeirja_)(_9u-a9jdfae90ej-e09!@aldjfa;'

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "danger"
login_manager.init_app(app)

user_manager = UserManager()

timeclock = TimeClock()

@login_manager.user_loader
def load_user(userid):
    return user_manager.get_user(userid)

@app.route("/", methods=["GET", "PUT"])
def webtime():
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

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("webtime"))
    form = RegisterForm()
    if form.validate_on_submit():
        if timeclock.register_user(form):
            return redirect(url_for("login"))
    return render_template("register.html", title="Registration", form=form)

@app.route("/login", methods=["GET", "POST"])
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

@app.route("/start", methods=["POST", "GET"])
@login_required
def start():
    # Get lists for Start page
    project_list = timeclock.get_list("projects")
    task_list = timeclock.get_list("tasks")
    note_list = timeclock.get_list("notes")

    form = StartForm()
    if form.validate_on_submit():
        if timeclock.start_timing(form):
            return redirect(url_for("webtime"))
    return render_template("start.html", title="Start Timing", form=form, 
        projects=project_list, tasks=task_list, notes=note_list)

@app.route("/stop", methods=["GET", "PUT"])
@login_required
def stop():
    if not timeclock.stop_timing():
        flash("There was an error stopping the timeclock", "danger")
        return redirect(url_for("webtime"))
    return redirect(url_for("webtime"))

@app.route("/adjust")
@login_required
def adjust():
    return render_template("adjust.html")

@app.route("/adjust/<string:item_type>/", methods=["GET", "POST"])
@login_required
def adjust_itemselect(item_type):
    if item_type == "time":
        form = DateSelectForm()
        if form.validate_on_submit():
            row_list = timeclock.get_daterange_rows(form)
            if row_list:
                for timelog_row in [timelog_row for timelog_row in row_list]:
                    timelog_row["start"] = (
                        timeclock.convert_timezone(
                            dt.strptime(timelog_row.get("start"), "%Y-%m-%dT%H:%M:%SZ"),
                            current_user.timezone
                        ).strftime("%Y-%m-%d %H:%M")
                    )
                    if timelog_row.get("stop"):
                        timelog_row["stop"] = (
                            timeclock.convert_timezone(
                                dt.strptime(timelog_row.get("stop"), "%Y-%m-%dT%H:%M:%SZ"),
                                current_user.timezone
                            ).strftime("%Y-%m-%d %H:%M")
                        )
                return render_template("adjust_itemselect.html", items=row_list, item_type=item_type)
        return render_template("adjust_dateselect.html", form=form)
    if item_type == "project":
        item_list = timeclock.get_projects()
    elif item_type == "task":
        item_list = timeclock.get_tasks()
    elif item_type == "note":
        item_list = timeclock.get_notes()
    return render_template("adjust_itemselect.html", items=item_list, item_type=item_type)

@app.route("/adjust/item/<string:item_type>/<int:id>", methods=["GET", "POST"])
@login_required
def adjust_item(item_type, id):
    if item_type == "project":
        item = [project for project in timeclock.get_projects() if project["projectid"] == id][0]
    elif item_type == "task":
        item = [task for task in timeclock.get_tasks() if task["taskid"] == id][0]
    elif item_type == "note":
        item = [note for note in timeclock.get_notes() if note["noteid"] == id][0]
    elif item_type == "time":
        item = [time for time in timeclock.date_range_rows if time["timelogid"] == str(id)][0]
    form = ItemEditForm()
    if form.validate_on_submit():
        if timeclock.update_item(form, item_type, id):
            flash("Item updated successfully!", "success")
            return redirect(url_for("adjust_itemselect", item_type=item_type))
    return render_template("adjust_item.html", form=form, item_type=item_type, item=item)

@app.route("/report", methods=["GET", "POST"])
@login_required
def report():
    form = DateSelectForm()
    if form.validate_on_submit():
        report_data = timeclock.process_daterange_rows(timeclock.get_daterange_rows(form), current_user.timezone)
        if type(report_data) != int:
            return render_template("report_result.html", title="Report Result", report_data=report_data)
        else:
            flash("No data for date range selected.", "danger")
    return render_template("report.html", title="Report Date Selection", form=form)

@app.route("/users")
@login_required
def users():
    form = UserForm()
    return render_template("users.html", user=current_user, form=form)

@app.route("/logout")
@login_required
def logout():
    timeclock.set_userid(0)
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("webtime"))