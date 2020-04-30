import requests
import pandas as pd

from dateutil import tz
from datetime import datetime as dt

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, login_required, current_user, logout_user, login_user

from flask_bcrypt import Bcrypt

from forms import LoginForm, RegisterForm, NewForm, StartForm
from models import MyUser, UserManager

app = Flask(__name__)
app.secret_key = b';aeirja_)(_9u-a9jdfae90ej-e09!@aldjfa;'

aws_route = "http://ec2-35-175-208-202.compute-1.amazonaws.com/api"

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "danger"
login_manager.init_app(app)

bcrypt = Bcrypt(app)

user_manager = UserManager()

@login_manager.user_loader
def load_user(userid):
    return user_manager.get_user(userid)

@app.route("/webtime", methods=["GET", "PUT"])
def webtime():
    message = "Click Start to start timing!"
    if current_user.is_authenticated:
        if current_user.timelogid != 0:
            cur_row_resp = requests.get(aws_route+"/timelog/"+str(current_user.timelogid))
            # ToDo: Handle all response status codes
            # ToDo: Build response code handler
            if cur_row_resp.status_code == 200:
                current_user.set_timelog_data(cur_row_resp.json())
                message = "Started {cname} - {pname} at {start}".format(
                    cname=current_user.client,
                    pname=current_user.project,
                    start=(
                        dt.strptime(current_user.start, "%Y-%m-%d %H:%M:%S")
                        .replace(tzinfo=tz.tzutc())
                        .astimezone(tz.tzlocal())
                        .strftime("%Y-%m-%d %H:%M")
                        )
                )
        elif current_user.stopped:
            stop = {
                "userid": str(current_user.userid),
                "clientid": str(current_user.clientid),
                "projectid": str(current_user.projectid),
                "start": current_user.start
                "stop": dt.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
            stop_resp = requests.put(aws_route+"/timelog/"+str(current_user.timelogid), json=stop)
            if stop_resp.status_code == 201:
                message = "Stopped timing {cname} - {pname}".format(
                    cname=current_user.client,
                    pname=current_user.project
                )
                current_user.reset_timelog_data()
    return render_template("webtime.html", title="PythonTimeClock", message=message)

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
            user_manager.add_user(cur_user.get_id(), cur_user)
            login_user(cur_user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("webtime"))
        else:
            flash("User Not Recognized.  Please check your info or Register an Account!", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/webtime/start", methods=["POST", "GET"])
@login_required
def start():
    cl_resp = requests.get(aws_route+"/clients")
    # ToDo: Handle all response codes
    if cl_resp.status_code == 200:
        cl_data = cl_resp.json()
        cl_df = pd.DataFrame()
        for client in cl_data:
            cl_df = cl_df.append(client, ignore_index=True)
    pr_resp = requests.get(aws_route+"/projects")
    if pr_resp.status_code == 200:
        pr_data = pr_resp.json()
        pr_df = pd.DataFrame()
        for project in pr_data:
            pr_df = pr_df.append(project, ignore_index=True)
    client_opts = cl_df["client_name"].tolist()
    client_ids = cl_df["clientid"].tolist()
    project_opts = pr_df["project_name"].tolist()
    project_ids = pr_df["projectid"].tolist()
    form = StartForm()
    if form.validate_on_submit():
        # Make sure user entered existing client
        if form.client.data in client_opts:
            client_exists = True
            clientid = client_ids[client_opts.index(form.client.data)]
        else:
            client_exists = False
        # Make sure user entered existing project
        if form.project.data in project_opts:
            project_exists = True
            projectid = project_ids[project_opts.index(form.project.data)]
        else:
            project_exists = False
        if client_exists and project_exists:
            timelog = {
                "userid": str(int(current_user.userid)),
                "clientid": str(int(clientid)),
                "projectid": str(int(projectid)),
                "start": dt.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "stop": "na"
            }
            tl_resp = requests.post(aws_route+"/timelog/users/"+str(current_user.userid), json=timelog)
            if tl_resp.status_code == 201:
                current_user.timelogid = tl_resp.json()["timelogid"]
                return redirect(url_for("webtime"))
    return render_template("start.html", form=form, client_opts=client_opts, project_opts=project_opts)

@app.route("/webtime/stop", methods=["GET", "PUT"])
@login_required
def stop():
    current_user.stopped = 1
    return redirect(url_for("webtime"))

@app.route("/webtime/new", methods=["POST", "GET"])
@login_required
def new():
    form = NewForm()
    if form.validate_on_submit():
        if form.new_client.data:
            resp = requests.post(aws_route+"/clients", json={"client_name": form.new_client.data})
            if resp == 201:
                client_success = True
            else:
                client_success = False
        else:
            no_client = True
        if form.new_project.data:
            resp = requests.post(aws_route+"/projects", json={"project_name": form.new_project.data})
            if resp == 201:
                project_success = True
            else:
                project_success = False
        else:
            no_project = True
        if (client_success or no_client) and (project_success or no_project):
            flash("New items successfully added!", "success")
            return redirect(url_for("start"))
        elif not client_success:
            flash("The client name you submitted already exists")
        elif not project_success:
            flash("The project name you submitted alread exists.")
    return render_template("new.html", form=form)

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

@login_required
@app.route("/users")
def users():
    return render_template("users.html")

@app.route("/webtime/logout")
def logout():
    logout_user()
    flash("You have successfully logged out.", "success")
    return redirect(url_for("webtime"))

if __name__ == "__main__":
    app.run(debug=True)