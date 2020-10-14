import sys
import requests
import json

import pandas as pd

from datetime import datetime as dt
from datetime import timedelta
from dateutil import tz
from flask import flash

from config import aws_route, bcrypt, db
from models import User


class TimeClock():

    def convert_timezone(self, my_time, to, orig="utc"):
        """Convert provided DateTime Object between UTC and Local Timezone
            @my_time-DateTime or Time Object: DateTime or Time to convert
            @to-string: timezone to convert to
            @orig-string: timezone to convert from
        returns DateTime Object or None if tz not supported.  Handle your own damn formatting.
        """
        return (my_time.replace(tzinfo=tz.tz.gettz(orig)).astimezone(tz.tz.gettz(to)))

    def register_user(self, form):
        new_user = User(
            form.user_name.data, 
            form.email.data,
            bcrypt.generate_password_hash(form.password.data),
            form.timezone.data)
        try: 
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except Exception as e:
            return None
    
    def login_user(self, form):
        user = User.query.filter(User.user_name == form.user_name.data).one_or_none()

        if user and bcrypt.check_password_hash(user.user_token, form.password.data):
            return user
        else:
            return
    
    def get_timerow(self, id):
        response = requests.get(aws_route + "/timelog/{id}".format(id=str(id)))
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    def get_projects(self):
        response = requests.get(aws_route + "/projects")
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def create_project(self, project_name):
        project = {"project_name": project_name}
        response = requests.post(aws_route + "/projects", params=project)
        if response.status_code == 201:
            return response.json()["projectid"]
        else:
            return None

    def get_tasks(self):
        response = requests.get(aws_route + "/tasks")
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def create_task(self, task_name):
        task = {"task_name": task_name}
        response = requests.post(aws_route + "/tasks", params=task)
        if response.status_code == 201:
            return response.json()["taskid"]
        else:
            return None

    def get_notes(self):
        response = requests.get(aws_route + "/notes")
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def create_note(self, note_name):
        note = {"note_name": note_name}
        response = requests.post(aws_route + "/notes", params=note)
        if response.status_code == 201:
            return response.json()["noteid"]
        else:
            return None

    def get_list(self, list_name):
        if list_name == "projects":
            self.projects = self.get_projects()
            return [project["project_name"] for project in self.projects]
        elif list_name == "tasks":
            self.tasks = self.get_tasks()
            return [task["task_name"] for task in self.tasks]
        elif list_name == "notes":
            self.notes = self.get_notes()
            return [note["note_name"] for note in self.notes]
    
    def update_item(self, form, item_type, id, user):
        if item_type == "project":
            project = {"project_name": form.project.data.lower()}
            response = requests.put(aws_route + "/projects/" + str(id), params=project)
            if response.status_code == 200:
                return 1
            elif response.status_code == 404:
                flash("Error. Project {} does not exist.".format(str(id)))
                return 0
            elif response.status_code == 409:
                flash("Error.  Project Name {} already exists.".format(form.project.data))
                return 0
            else:
                flash("Error Updating Project: " + response.text, "danger")
                return 0
        elif item_type == "task":
            task = {"task_name": form.task.data.lower()}
            response = requests.put(aws_route + "/tasks/" + str(id), params=task)
            if response.status_code == 200:
                return 1
            elif response.status_code == 404:
                flash("Error. Task {} does not exist.".format(str(id)))
                return 0
            elif response.status_code == 409:
                flash("Error.  Task Name {} already exists.".format(form.task.data))
                return 0
            else:
                flash("Error Updating Task: " + response.text, "danger")
                return 0
        elif item_type == "note":
            note = {"note_name": form.note.data.lower()}
            response = requests.put(aws_route + "/notes/" + str(id), params=note)
            if response.status_code == 200:
                return 1
            elif response.status_code == 404:
                flash("Error. Note {} does not exist.".format(str(id)))
                return 0
            elif response.status_code == 409:
                flash("Error.  Note Name {} already exists.".format(form.note.data))
                return 0
            else:
                flash("Error Updating Note: " + response.text, "danger")
                return 0
        elif item_type == "time":
            if (form.project.data.lower() in self.get_list("projects")):
                projectid = self.projects[[project["project_name"] for project in self.projects].index(form.project.data.lower())]["projectid"]
            else:
                projectid = self.create_project(form.project.data.lower())

            if (form.task.data.lower() in self.get_list("tasks")):
                taskid = self.tasks[[task["task_name"] for task in self.tasks].index(form.task.data.lower())]["taskid"]
            else:
                taskid = self.create_task(form.task.data.lower())

            if (form.note.data.lower() in self.get_list("notes")):
                noteid = self.notes[[note["note_name"] for note in self.notes].index(form.note.data.lower())]["noteid"]
            else:
                noteid = self.create_note(form.note.data.lower())

            if projectid and taskid and noteid:
                
                if form.stop.data == "None":
                    timelog = {
                            "userid": str(user.userid),
                            "projectid": str(projectid),
                            "taskid": str(taskid),
                            "noteid": str(noteid),
                            "start": self.convert_timezone(
                                dt.strptime(form.start.data, "%Y-%m-%d %H:%M"),
                                "utc", orig=user.timezone
                            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "stop": "na"
                        }                   
                else:
                    timelog = {
                            "userid": str(user.userid),
                            "projectid": str(projectid),
                            "taskid": str(taskid),
                            "noteid": str(noteid),
                            "start": self.convert_timezone(
                                dt.strptime(form.start.data, "%Y-%m-%d %H:%M"),
                                "utc", orig=user.timezone
                            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "stop": self.convert_timezone(
                                dt.strptime(form.stop.data, "%Y-%m-%d %H:%M"),
                                "utc", orig=user.timezone
                            ).strftime("%Y-%m-%dT%H:%M:%SZ")
                        }

                old_timelog = self.get_timerow(id)
                    
                response = requests.put(aws_route + "/timelog/" + str(id), json=timelog)
                if response.status_code == 200:
                    if form.adjacent.data == True:
                        if old_timelog:
                            # Need to build search for timelog row by userid + start or stop time
                            # if start match, update with form.stop.data
                            # if stop match, update with form.start.data
                            pass
                        else:
                            flash("Error getting timelog row for adjacent check.", "danger")
                    if item_type == "time":
                        return timelog
                    else:
                        return 1
                else:
                    flash("Error Updating Timelog Row", "danger")
                    return 0

    def start_timing(self, form, user, current_timelog=None, stop=0):
        if (form.project.data.lower() in self.get_list("projects")):
            projectid = self.projects[[project["project_name"] for project in self.projects].index(form.project.data.lower())]["projectid"]
        else:
            projectid = self.create_project(form.project.data.lower())

        if (form.task.data.lower() in self.get_list("tasks")):
            taskid = self.tasks[[task["task_name"] for task in self.tasks].index(form.task.data.lower())]["taskid"]
        else:
            taskid = self.create_task(form.task.data.lower())

        if (form.note.data.lower() in self.get_list("notes")):
            noteid = self.notes[[note["note_name"] for note in self.notes].index(form.note.data.lower())]["noteid"]
        else:
            noteid = self.create_note(form.note.data.lower())

        if projectid and taskid and noteid:
            timelog = {
                    "userid": str(user.userid),
                    "projectid": str(projectid),
                    "taskid": str(taskid),
                    "noteid": str(noteid),
                    "start": dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "stop": "na"
                }

            tl_resp = requests.post(aws_route + "/timelog", json=timelog)
            if tl_resp.status_code == 201:
                if stop:
                    current_timelog["stop"] = timelog.get("start")
                    self.stop_timing(timelog=current_timelog, has_stop=True)
                return tl_resp.json()
            else:
                flash("Something went wrong with timelog post", "danger")
                return None
        else:
            flash("Something went wrong with id assignment", "danger")
            return None
        
    def stop_timing(self, timelog, has_stop=False):
        # Stop=None allows Start Timing to supply stop time to keep start/stop values in sync while
        # allowing stop timing to stop at the current time.
        if not has_stop:
            timelog["stop"] = dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        response = requests.put(aws_route + "/timelog/" + str(timelog.get("timelogid")), json=timelog)
        if response.status_code == 200:
            return 1
        else:
            return 0

    def get_daterange_rows(self, form, user):
        range_begin = (self.convert_timezone(
            dt.combine(
                form.range_begin.data,
                dt.min.time()
            ),
            "utc", orig=user.timezone
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        if form.range_end.data:
            range_end = (self.convert_timezone(
                dt.combine(
                    form.range_end.data,
                    dt.max.time()
                ),
                "utc", orig=user.timezone
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        else:
            range_end = (self.convert_timezone(
                dt.combine(
                    form.range_begin.data,
                    dt.max.time()
                ),
                "utc", orig=user.timezone
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        query = {
            "userid": user.userid,
            "range_begin": range_begin,
            "range_end": range_end
            }
        response = requests.get(aws_route+"/timelog/daterange", params=query)
        if response.status_code == 200:
            date_range_rows = json.loads(response.json())
            for timelogrow in date_range_rows["rows"]:
                timelogrow["start"] = self.convert_timezone(
                    dt.strptime(timelogrow["start"] ,"%Y-%m-%dT%H:%M:%SZ"),
                    user.timezone
                    ).strptime("%Y-%m-%d %H:%M")
                if timelogrow.get("stop"):
                    timelogrow["stop"] = self.convert_timezone(
                    dt.strptime(timelogrow["stop"] ,"%Y-%m-%dT%H:%M:%SZ"),
                    user.timezone
                    ).strptime("%Y-%m-%d %H:%M")
            return date_range_rows["rows"]
        else:
            flash("Error reading rows with dates submitted.", "danger")
            return 0

    def process_daterange_rows(self, daterange_rows, timezone, cur_tlid):
        if type(daterange_rows) == int:
            return 0
        daterange = pd.DataFrame()
        for row in daterange_rows:
            daterange = daterange.append(row, ignore_index=True)

        # preprocess: Convert times; Fill current timelog stop with current time; fill report_date
        for i, row in daterange.iterrows():
            daterange.at[i, "report_date"] = (
                self.convert_timezone(
                    dt.strptime(row["start"], "%Y-%m-%dT%H:%M:%SZ"), 
                    timezone
                    ).strftime("%Y-%m-%d")
            )   
            if row["timelogid"] == str(cur_tlid):
                daterange.at[i, "hours"] = (dt.utcnow() - dt.strptime(row["start"], "%Y-%m-%dT%H:%M:%SZ")).seconds / 3600
            elif not pd.isna(row["stop"]):
                daterange.at[i, "hours"] = (dt.strptime(row["stop"], "%Y-%m-%dT%H:%M:%SZ") - dt.strptime(row["start"], "%Y-%m-%dT%H:%M:%SZ")).seconds / 3600

        # Sum rows by date-project-task-note
        sum_df = daterange[["report_date", "project_name", "task_name", "note_name", "hours"]].groupby(by=[
            "report_date", "project_name", "task_name", "note_name"]).sum().reset_index()

        # Round hours
        sum_df["hours"] = sum_df["hours"].apply(lambda x: round(x, 1))

        # Sum hours by day and add to sum_df
        sum_row = sum_df[["report_date", "hours"]].groupby("report_date").sum().reset_index()
        sum_row["project_name"] = "date_total_hours"
        sum_df = sum_df.append(sum_row, ignore_index=True)

        return sum_df

    
