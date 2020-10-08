from dateutil import tz
from datetime import datetime as dt

from flask import render_template, url_for, redirect, request, flash, session
from flask_login import login_user, current_user, logout_user, login_required

from forms import (RegisterForm, LoginForm, StartForm, DateSelectForm, ItemEditForm, UserForm)

from config import app
from timeclock import TimeClock

timeclock = TimeClock()

@app.route("/", methods=["GET", "PUT"])
def webtime():
    message = "Click Start to start timing!"
    if "stop" in session:
        message = "Stopped tracking {pname} - {tname} \n {nname}".format(
            pname=session["project"].get("name"),
            tname=session["task"].get("name"),
            nname=session["note"].get("name")
        )
        timeclock.reset_timelog_fields()
    elif "timelogid" in session:
        message = "Started {pname} - {tname} \n{nname} at {start}".format(
            pname=session["project"].get("name"),
            tname=session["task"].get("name"),
            nname=session["note"].get("name"),
            start=session["start"]
        )
    return render_template("webtime.html", title="PythonTimeClock", message=message)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("webtime"))
    form = RegisterForm()
    if form.validate_on_submit():
        if timeclock.register_user(form):
            flash("Account Created for {}!  Please log in.".format(form.user_name.data), "success")
            return redirect(url_for("login"))
        else:
            flash("Error creating account.  Please try again.", "danger")
    return render_template("register.html", title="Registration", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users"))
    form = LoginForm()
    if form.validate_on_submit():
        new_user = timeclock.login_user(form)
        if new_user:
            login_user(new_user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("webtime"))
        else:
            flash("User not recognized.  Please check your info or Register an Account!", "danger")
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
        if "timelogid" in session:
            current_timelog = {
                "userid": current_user.userid,
                "timelogid": session["timelogid"],
                "projectid": session["projectid"].get("id"),
                "taskid": session["taskid"].get("id"),
                "noteid": session["noteid"].get("id"),
                "start": session["start"],
            }
            timelog = timeclock.start_timing(form, current_user, current_timelog=current_timelog, stop=1)
        else:
            timelog = timeclock.start_timing(form, current_user)
        if timelog:
            session["timelogid"] = timelog.get("timelogid")
            session["project"] = {"id": timelog.get("projectid"), "name": form.project.data}
            session["task"] = {"id": timelog.get("taskid"), "name": form.task.data}
            session["note"] = {"id": timelog.get("noteid"), "name": form.note.data}
            session["start"] = timeclock.convert_timezone(dt.strptime(timelog.get("start"), "%Y-%m-%dT%H:%M:%SZ"), current_user.timezone).strftime("%Y-%m-%d %H:%M")
            session.pop("stop", None)
            return redirect(url_for("webtime"))
    return render_template("start.html", title="Start Timing", form=form, 
        projects=project_list, tasks=task_list, notes=note_list)

@app.route("/stop", methods=["GET", "PUT"])
@login_required
# API call works, so the problem has to be with the values I'm submitting.
def stop():
    if "timelogid" in session:
        current_timelog = {
                "userid": current_user.userid,
                "timelogid": session["timelogid"],
                "projectid": session["projectid"].get("id"),
                "taskid": session["taskid"].get("id"),
                "noteid": session["noteid"].get("id"),
                "start": timeclock.convert_timezone(datetime.strptime(session["start"], "%Y-%m-%d %H:%M"), "utc", orig=current_user.timezone).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        if not timeclock.stop_timing(current_timelog):
            flash("There was an error stopping the timeclock.", "danger")
        else:
            session.pop("timelogid", None)
            session.pop("project", None)
            session.pop("task", None)
            session.pop("note", None)
            session.pop("start", None)
            session["stop"] = 1
    else:
        flash("Not currently timing anything.", "danger")
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
                            session.get("timezone")
                        ).strftime("%Y-%m-%d %H:%M")
                    )
                    if timelog_row.get("stop"):
                        timelog_row["stop"] = (
                            timeclock.convert_timezone(
                                dt.strptime(timelog_row.get("stop"), "%Y-%m-%dT%H:%M:%SZ"),
                                session.get("timezone")
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
    logout_user()
    session.pop("timelogid", None)
    session.pop("project", None)
    session.pop("task", None)
    session.pop("note", None)
    session.pop("start", None)
    session.pop("stop", None)
    flash("You have successfully logged out.", "success")
    return redirect(url_for("webtime"))
