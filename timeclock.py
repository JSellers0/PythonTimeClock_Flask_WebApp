import sys
import requests
import json

import pandas as pd

from datetime import datetime as dt
from datetime import timedelta
from dateutil import tz
from itsdangerous import Serializer
from flask import flash

from config import aws_route

s = Serializer("16bOEuoyrWn1DxiIXWVsG9")

class TimeClock():
    def __init__(self):
        self.userid = None
        self.reset_timelog_fields()

    def convert_timezone(self, my_time, to):
        """Convert provided DateTime Object between UTC and Local Timezone
            :my_time - DateTime Object for conversion
            :to - timezone to convert to ("utc" or "local")
        returns DateTime Object or None if tz not supported.  Handle your own damn formatting.
        """
        if to == "utc":
            return (
                my_time
                .replace(tzinfo=tz.tzlocal())
                .astimezone(tz.tzutc())
            )

        else:
            return (
                my_time
                .replace(tzinfo=tz.tzutc())
                .astimezone(tz.tz.gettz(to))
            )

    def reset_timelog_fields(self):
        """ Reset timelog fields to default no value"""
        self.timelogid = 0
        self.project = {}
        self.task = {}
        self.note = {}
        self.start = None
        self.stop = 0

        return 0

    def set_userid(self, userid):
        self.userid = str(userid)
        return 0

    def set_timelog_fields(self, timelog, form):
        self.timelogid = timelog.get("timelogid")
        self.project = {
            "name": form.project.data.lower(),
            "id": timelog.get("projectid")}
        self.task = {
            "name": form.task.data.lower(),
            "id": timelog.get("taskid")}
        self.note = {
            "name": form.note.data.lower(),
            "id": timelog.get("noteid")}
        self.start = timelog.get("start")
        self.stop = 0
        #self.convert_timezone(dt.strptime(timelog.get("start"), "%Y-%m-%dT%H:%M:%SZ"), "local").strftime("%Y-%m-%d %H:%M")

    def register_user(self, form):
        user = {
            "user_name": form.user_name.data,
            "email" : form.email.data,
            "user_token": s.dumps([form.user_name.data, form.password.data]),
            "timezone": form.timezone.data
        }
        resp = requests.post(aws_route + "/users", json=user)
        if resp.status_code == 201:
            flash("Account created for {}!  Please Log In."
                .format(form.user_name.data), 
                "success"
            )
            return 1
        else:
            # ToDo: Add more responses for errors.
            return None

    def get_user_by_token(self, token):
        user = {"user_token": token}

        response = requests.post(aws_route + "/users/token", json=user)
        if response.status_code == 200:
            return response.json()
    
    def login_user(self, form):
        user = {"user_token": s.dumps([form.user_name.data, form.password.data])}
        response = requests.post(aws_route + "/users/token", json=user)
        if response.status_code == 200:
            return response.json(), user.get("user_token")
        else:
            flash("User Not Recognized.  Please check your info or Register an Account!", "danger")
            return None
    
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
    
    def update_item(self, form, item_type, id):
        if item_type == "project":
            project = {
                "projectid": id,
                "project_name": form.project.data
            }
            response = requests.put(aws_route + "/projects/" + str(id), json=project)
            if response.status_code == 200:
                return 1
            else:
                flash("Error Updating Note", "danger")
                return 0
        elif item_type == "task":
            task = {
                "taskid": id,
                "task_name": form.task.data
            }
            response = requests.put(aws_route + "/tasks/" + str(id), json=task)
            if response.status_code == 200:
                return 1
            else:
                flash("Error Updating Note", "danger")
                return 0
        elif item_type == "note":
            note = {
                "noteid": id,
                "note_name": form.note.data
            }
            response = requests.put(aws_route + "/notes/" + str(id), json=note)
            if response.status_code == 200:
                return 1
            else:
                flash("Error Updating Note", "danger")
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
                
                if form.stop.data == "1900-01-01 00:00" or form.stop.data.replace(" ", "") == "":
                    timelog = {
                            "userid": str(self.userid),
                            "projectid": str(projectid),
                            "taskid": str(taskid),
                            "noteid": str(noteid),
                            "start": self.convert_timezone(
                                dt.strptime(form.start.data, "%Y-%m-%d %H:%M"),
                                "utc"
                            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "stop": "na"
                        }                   
                else:
                    timelog = {
                            "userid": str(self.userid),
                            "projectid": str(projectid),
                            "taskid": str(taskid),
                            "noteid": str(noteid),
                            "start": self.convert_timezone(
                                dt.strptime(form.start.data, "%Y-%m-%d %H:%M"),
                                "utc"
                            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "stop": self.convert_timezone(
                                dt.strptime(form.stop.data, "%Y-%m-%d %H:%M"),
                                "utc"
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

                    if id == self.timelogid:
                        self.start = self.convert_timezone(
                                dt.strptime(form.start.data, "%Y-%m-%d %H:%M"),
                                "utc"
                            ).strftime("%Y-%m-%dT%H:%M:%SZ")
                    return 1
                else:
                    flash("Error Updating Timelog Row", "danger")
                    return 0
        return 1

    def start_timing(self, form):
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
                    "userid": str(self.userid),
                    "projectid": str(projectid),
                    "taskid": str(taskid),
                    "noteid": str(noteid),
                    "start": dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "stop": "na"
                }

            tl_resp = requests.post(aws_route + "/timelog", json=timelog)
            if tl_resp.status_code == 201:
                if self.timelogid:
                    self.stop_timing(stop=timelog.get("start"))
                self.set_timelog_fields(tl_resp.json(), form)
                return 1
            else:
                flash("Something went wrong with timelog post", "danger")
                return None
        else:
            flash("Something went wrong with id assignment", "danger")
            return None
        
    def stop_timing(self, stop=None):
        if stop:
            timelog = {
                "userid": str(self.userid),
                "projectid": str(self.project.get("id")),
                "taskid": str(self.task.get("id")),
                "noteid": str(self.note.get("id")),
                "start": self.start,
                "stop": stop
            }
        else:
            timelog = {
                "userid": str(self.userid),
                "projectid": str(self.project.get("id")),
                "taskid": str(self.task.get("id")),
                "noteid": str(self.note.get("id")),
                "start": self.start,
                "stop": dt.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        response = requests.put(aws_route + "/timelog/" + str(self.timelogid), json=timelog)
        if response.status_code == 200:
            self.stop = 1
            return 1
        else:
            return 0

    def get_daterange_rows(self, form):
        range_begin = (self.convert_timezone(
            dt.combine(
                form.range_begin.data,
                dt.min.time()
            ),
            "utc"
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        if form.range_end.data:
            range_end = (self.convert_timezone(
                dt.combine(
                    form.range_end.data,
                    dt.max.time()
                ),
                "utc"
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        else:
            range_end = (self.convert_timezone(
                dt.combine(
                    form.range_begin.data,
                    dt.max.time()
                ),
                "utc"
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        query = {
            "userid": self.userid,
            "range_begin": range_begin,
            "range_end": range_end
            }
        response = requests.get(aws_route+"/timelog/daterange", params=query)
        if response.status_code == 200:
            date_range_rows = json.loads(response.json())
            self.date_range_rows = date_range_rows["rows"]
            return date_range_rows["rows"]
        else:
            flash("Error reading rows with dates submitted.", "danger")
            return 0

    def process_daterange_rows(self, daterange_rows, timezone):
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
            if row["timelogid"] == str(self.timelogid):
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

    