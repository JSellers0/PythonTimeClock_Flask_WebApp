# ToDo: Restructure for Web App

import sys
import requests
import json

from datetime import datetime as dt
from datetime import timedelta
from dateutil import tz

from flask import flash

from models import MyUser

from config import aws_route

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

        elif to == "local":
            return (
                my_time
                .replace(tzinfo=tz.tzutc())
                .astimezone(tz.tzlocal())
            )

        else:
            return None

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
        #self.convert_timezone(dt.strptime(timelog.get("start"), "%Y-%m-%dT%H:%M:%SZ"), "local").strftime("%Y-%m-%d %H:%M")

    def register_user(self, form):
        user = {
            "user_name": form.user_name.data,
            "email" : form.email.data,
            "password": form.password.data
        }
        resp = requests.post(aws_route+"/users", json=user)
        if resp.status_code == 201:
            flash("Account created for {}!  Please Log In.", "success")
            return 1
        else:
            return None
    
    def login_user(self, form):
        user = {
            "user_name": form.user_name.data,
            "password" : form.password.data
            }
        response = requests.post(aws_route + "/users/name", json=user)
        if response.status_code == 200:
            self.set_userid(response.json()["userid"])
            return MyUser(response.json())
        else:
            flash("User Not Recognized.  Please check your info or Register an Account!", "danger")
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
            print(timelog)
            tl_resp = requests.post(aws_route + "/timelog", json=timelog)
            print(tl_resp.status_code)
            if tl_resp.status_code == 201:
                if self.timelogid:
                    self.stop_timing(stop_time=timelog.get("start"))
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
        print(json.dumps(timelog))
        print(aws_route + "/timelog/" + str(self.timelogid))
        response = requests.put(aws_route + "/timelog/" + str(self.timelogid), json=timelog)
        print(response.url)
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
                    dt.min.time()
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
            rows = response.json()
        else:
            flash("Error reading rows with dates submitted.", "danger")
            return 0

    def run(self, db, ui):
        DB = db
        UI = ui
        state = self.initialize_states()
        main_window = UI.get_main_window((75, 0), state["message1"], state["message2"])
        while True:
            event, values = main_window.read(timeout=10)
            if event in (None, "Exit"):
                if state["timelogid"] > 0:
                    state = self.stop_timing(state, DB)
                main_window.close()
                break

            elif event == "Report":
                report_date_window = UI.get_report_date_window(
                    main_window.current_location(),
                    datetime.today().strftime("%Y-%m-%d"),
                    datetime.today().strftime("%Y-%m-%d"),
                )
                main_window.close()
                while True:
                    if state["return_to_main"]:
                        state["return_to_main"] = False
                        break
                    report_date_event, report_date_values = report_date_window.read(
                        timeout=10
                    )
                    if report_date_event == None:
                        if state["timelogid"] > 0:
                            state = self.stop_timing(state, DB)
                        DB.close()
                        sys.exit()
                    elif report_date_event == "Cancel":
                        main_window = UI.get_main_window(
                            report_date_window.current_location(),
                            state["message1"],
                            state["message2"],
                        )
                        report_date_window.close()
                        break
                    
                    elif report_date_event == "Submit":
                        report_df = DB.getTableItems(
                            "timelog",
                            self.convert_to_utc(report_date_values["start"] + " 00:00"),
                            self.convert_to_utc(report_date_values["stop"] + " 23:59"),
                        )
                        # If the current timelog row is in the report, set the stop time
                        # to the current time for calculations
                        if len(report_df) == 0:
                            report_date_window["error_message"].Update(visible=True)
                        else:
                            if (
                                len(report_df[report_df.timelogid == state["timelogid"]])
                                == 1
                            ):
                                report_df.loc[
                                    report_df.timelogid == state["timelogid"], ("stop")
                                ] = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

                            # Check for other null stop values prior to reporting calculations
                            if report_df["stop"].isna().sum() > 0:
                                gap_df = report_df.loc[report_df.stop.isna()]
                                gap_df["date"] = gap_df["start"].apply(
                                    lambda x: self.convert_to_local(x, date_only=True)
                                )
                                state["report_gap_dates"] = gap_df["date"].unique().tolist()
                                gap_df = None
                                report_df.dropna(inplace=True)

                            report_df["diff"] = report_df["stop"].apply(
                                lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M")
                            ) - report_df["start"].apply(
                                lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M")
                            )
                            report_df["date"] = report_df["start"].apply(
                                lambda x: self.convert_to_local(x, date_only=True)
                            )
                            summary_df = (
                                report_df[["date", "client_name", "project_name", "diff"]]
                                .groupby(by=["date", "client_name", "project_name"])
                                .sum()
                            )
                            summary_df.reset_index(inplace=True)
                            # Convert Diff to Hours:Minutes
                            summary_df["diff"] = summary_df["diff"].apply(
                                lambda x: str(x)[
                                    str(x).find("d") + len("days ") : len(str(x)) - 3
                                ]
                            )
                            total_time = (
                                report_df[["date", "diff"]].groupby(by=["date"]).sum()
                            )
                            total_time.reset_index(inplace=True)
                            # Convert Total Time Diff to Hours:Minutes
                            total_time["diff"] = total_time["diff"].apply(
                                lambda x: str(x)[
                                    str(x).find("d") + len("days ") : len(str(x)) - 3
                                ]
                            )

                            i = 0
                            dates = total_time.date.unique().tolist()
                            report_window = UI.get_report_output_window(
                                report_date_window.current_location(),
                                summary_df.loc[summary_df.date == dates[i]],
                                total_time.loc[total_time.date == dates[i]],
                                i,
                            )
                            report_date_window.close()
                            while True:
                                report_event, report_values = report_window.read(timeout=10)
                                if report_event == None:
                                    if state["timelogid"] > 0:
                                        state = self.stop_timing(state, DB)
                                    DB.close()
                                    sys.exit()
                                
                                elif report_event == "back":
                                    report_date_window = UI.get_report_date_window(
                                        report_window.current_location(),
                                        report_date_values["start"],
                                        report_date_values["stop"],
                                    )
                                    report_window.close()
                                    break
                                
                                elif report_event == "increment":
                                    if i + 1 < len(dates):
                                        i += 1
                                        # TODO: Check date against Gap Dates.  Update window message if necessary.
                                        report_window2 = report_window
                                        report_window = UI.get_report_output_window(
                                            report_window2.current_location(),
                                            summary_df.loc[summary_df.date == dates[i]],
                                            total_time.loc[total_time.date == dates[i]],
                                            i,
                                        )
                                        report_window2.close()
                                elif report_event == "decrement":
                                    if i - 1 >= 0:
                                        i -= 1
                                        report_window2 = report_window
                                        report_window = UI.get_report_output_window(
                                            report_window2.current_location(),
                                            summary_df.loc[summary_df.date == dates[i]],
                                            total_time.loc[total_time.date == dates[i]],
                                            i,
                                        )
                                        report_window2.close()
                                
                                elif report_event == "main":
                                    main_window = UI.get_main_window(
                                        report_window.current_location(),
                                        state["message1"],
                                        state["message2"],
                                    )
                                    report_window.close()
                                    state["return_to_main"] = True
                                    break

            elif event == "Adjust":
                adjust_window = UI.get_adjustment_main_window(
                    main_window.current_location()
                )
                main_window.close()
                while True:
                    adjust_event, adjust_values = adjust_window.read(timeout=10)
                    if adjust_event == None:
                        if state["timelogid"] > 0:
                            state = self.stop_timing(state, DB)
                        DB.close()
                        sys.exit()
                    
                    elif adjust_event == "Close":
                        state["adjust_view"] = ""
                        main_window = UI.get_main_window(
                            adjust_window.current_location(),
                            state["message1"],
                            state["message2"],
                        )
                        adjust_window.close()
                        break
                    
                    elif adjust_event == "timelog":
                        state["adjust_view"] = adjust_event
                        adjust_select_window = UI.get_adjustment_timestamp_window(
                            adjust_window.current_location(),
                            self.convert_to_local(
                                datetime.utcnow().strftime("%Y-%m-%d %H:%M"), 
                                date_only=True
                                )
                        )
                        adjust_window.close()
                        while True:
                            (
                                adjust_select_event,
                                adjust_select_values,
                            ) = adjust_select_window.read(timeout=10)
                            if adjust_select_event == None:
                                if state["timelogid"] > 0:
                                    state = self.stop_timing(state, DB)
                                DB.close()
                                sys.exit()
                            
                            elif adjust_select_event == "Back":
                                adjust_window = UI.get_adjustment_main_window(
                                    adjust_select_window.current_location()
                                )
                                adjust_select_window.close()
                                state["adjust_view"] = ""
                                break
                            
                            elif adjust_select_event == "Submit":
                                state["adjust_date"] = adjust_select_values["date_input"]
                                break
                    
                    elif adjust_event in ("client", "project"):
                        state["adjust_view"] = adjust_event

                    if state["adjust_view"]:
                        if state["adjust_view"] == "timelog":
                            adjust_df = DB.getTableItems(
                                table="timelog",
                                start_date=self.convert_to_utc(
                                    adjust_select_values["date_input"] + " 00:00"
                                ),
                                end_date=self.convert_to_utc(
                                    adjust_select_values["date_input"] + " 23:59"
                                ),
                            )
                            adjust_df.fillna("2001-01-01 06:01", inplace=True)
                            adjust_df["start"] = adjust_df["start"].apply(
                                lambda x: self.convert_to_local(x)
                            )
                            adjust_df["stop"] = adjust_df["stop"].apply(
                                lambda x: self.convert_to_local(x)
                            )
                            adjust_result_window = UI.get_adjustment_results_window(
                                adjust_select_window.current_location(),
                                state["adjust_view"],
                                adjust_df,
                            )
                            adjust_select_window.close()
                        else:
                            adjust_df = DB.getTableItems(state["adjust_view"])
                            adjust_result_window = UI.get_adjustment_results_window(
                                adjust_window.current_location(),
                                state["adjust_view"],
                                adjust_df,
                            )
                            adjust_window.close()
                        while True:
                            adjustment_event, adjustment_values = adjust_result_window.read(
                                timeout=10
                            )
                            if adjustment_event == None:
                                if state["timelogid"] > 0:
                                    state = self.stop_timing(state, DB)
                                DB.close()
                                sys.exit()
                            
                            elif adjustment_event == "Close":
                                adjust_window = UI.get_adjustment_main_window(
                                    adjust_result_window.current_location()
                                )
                                state["adjust_view"] = ""
                                adjust_result_window.close()
                                break
                            
                            elif adjustment_event == "insert":
                                if state["adjust_view"] == "timelog":
                                    row = {"start": state["adjust_date"], "stop": state["adjust_date"]}
                                    insert_window = UI.get_update_window(adjust_result_window.current_location(),
                                                                         "insert",
                                                                         row,
                                                                         DB.getTableItems("client")["client_name"].tolist(),
                                                                         DB.getTableItems("project")["project_name"].tolist(),
                                                                         )
                                    adjust_result_window.close()
                                else:
                                    insert_window = UI.get_new_window(adjust_result_window.current_location(), state["adjust_view"])
                                    adjust_result_window.close()
                                while True:
                                    insert_event, insert_values = insert_window.read(timeout=10)
                                    if insert_event == None:
                                        if state["timelogid"] > 0:
                                            state = self.stop_timing(state, DB)
                                        DB.close()
                                        sys.exit()
                                    
                                    elif insert_event == "Cancel":
                                        adjust_result_window = UI.get_adjustment_results_window(
                                            insert_window.current_location(),
                                            state["adjust_view"],
                                            adjust_df,
                                        )
                                        insert_window.close()
                                        break
                                    elif insert_event == "Submit":
                                        # DB Insert Row
                                        if state["adjust_view"] == "timelog":
                                            item = {"start": insert_values["start"],
                                                    "stop": insert_values["stop"],
                                                    "projectid": DB.getTableItemID(insert_values["project"][0], "project"),
                                                    "clientid": DB.getTableItemID(insert_values["client"][0], "client")
                                            
                                                }
                                        elif state["adjust_view"] == "client":
                                            item = insert_values["new_client"]
                                        elif state["adjust_view"] == "project":
                                            item = insert_values["new_project"]
                                        DB.insert_table_item(item, state["adjust_view"])
                                        if state["adjust_view"] == "timelog":
                                            adjust_df = adjust_df = DB.getTableItems(
                                                state["adjust_view"],
                                                self.convert_to_utc(
                                                    adjust_select_values["date_input"] + " 00:00"
                                                ),
                                                self.convert_to_utc(
                                                    adjust_select_values["date_input"] + " 23:59"
                                                ),
                                            )
                                        else:
                                            adjust_df = DB.getTableItems(state["adjust_view"])
                                        adjust_result_window = UI.get_adjustment_results_window(
                                            insert_window.current_location(),
                                            state["adjust_view"],
                                            adjust_df,
                                        )
                                        insert_window.close()
                                        break

                            elif "Update" in adjustment_event:
                                row = adjust_df.iloc[
                                    int(adjustment_event[len("Update ") :])
                                ]
                                update_window = UI.get_update_window(
                                    adjust_result_window.current_location(),
                                    state["adjust_view"],
                                    row,
                                    DB.getTableItems("client")["client_name"].tolist(),
                                    DB.getTableItems("project")["project_name"].tolist(),
                                )
                                adjust_result_window.close()
                                while True:
                                    update_event, update_values = update_window.read(
                                        timeout=10
                                    )
                                    if update_event == None:
                                        if state["timelogid"] > 0:
                                            state = self.stop_timing(state, DB)
                                        DB.close()
                                        sys.exit()
                                    
                                    elif update_event == "Cancel":
                                        adjust_result_window = UI.get_adjustment_results_window(
                                            update_window.current_location(),
                                            state["adjust_view"],
                                            adjust_df,
                                        )
                                        update_window.close()
                                        break
                                    
                                    elif update_event == "Submit":
                                        if state["adjust_view"] == "timelog":
                                            if (
                                                update_values["start"] <= update_values["stop"]
                                                or update_values["stop"] == ""
                                            ):
                                                # If Start/Stop changed, ask about adjacent timestamps
                                                if update_values["start"] != row["start"]:
                                                    print("Start Adjacent Check")

                                                if update_values["stop"] != row["stop"]:
                                                    print("Stop Adjacent Check")

                                                # Set timelogid in update_values
                                                update_values["timelogid"] = row["timelogid"]
                                                # If the updated timelog row is the current row, 
                                                # then make sure we adjust the
                                                # State values for the main window message
                                                # Will want to do a similar check if we do the 
                                                # Start Adjacent Update
                                                if (
                                                    state["timelogid"]
                                                    == update_values["timelogid"]
                                                ):
                                                    state["start_time"] = update_values["start"]
                                                    state["client"] = update_values[
                                                        "client"
                                                    ][0]
                                                    state["project"] = update_values[
                                                        "project"
                                                    ][0]
                                                    state[
                                                        "message1"
                                                    ] = "Tracking {} - {}".format(
                                                        state["client"], state["project"]
                                                    )
                                                    state["message2"] = "since {}".format(
                                                        state["start_time"]
                                                    )

                                                update_values["start"] = self.convert_to_utc(
                                                    update_values["start"]
                                                )
                                                if not update_values["stop"] == "":
                                                    update_values["stop"] = self.convert_to_utc(
                                                        update_values["stop"]
                                                    )
                                                DB.update_timelog_row(update_values)
                                                adjust_df = DB.getTableItems(
                                                    "timelog",
                                                    self.convert_to_utc(
                                                        state["adjust_date"] + " 00:00"
                                                    ),
                                                    self.convert_to_utc(
                                                        state["adjust_date"] + " 23:59"
                                                    ),
                                                )
                                                adjust_df.fillna(
                                                    "2001-01-01 06:01", inplace=True
                                                )
                                                adjust_df["start"] = adjust_df["start"].apply(
                                                    lambda x: self.convert_to_local(x)
                                                )
                                                adjust_df["stop"] = adjust_df["stop"].apply(
                                                    lambda x: self.convert_to_local(x)
                                                )
                                            else:
                                                update_window["error_message"].Update(
                                                    visible=True
                                                )
                                        else:
                                            if not DB.check_table_item_exists(state["adjust_view"], update_values[0]):
                                                item = {"itemid": row[state["adjust_view"]+"ID"], "field": state["adjust_view"] + "_name", "value": update_values[0]}
                                                print(item)
                                                DB.update_table_item(item, state["adjust_view"])
                                                adjust_df = DB.getTableItems(state["adjust_view"])
                                        adjust_result_window = UI.get_adjustment_results_window(
                                                    update_window.current_location(), state["adjust_view"], adjust_df
                                                )
                                        update_window.close()
                                        break

            elif event == "Stop":
                if state["timelogid"] > 0:
                    state = self.stop_timing(state, DB)
                else:
                    state["message1"] = "Not currently tracking."
                    state["message2"] = "Click Start to begin."
                main_window["message1"].Update(value=state["message1"])
                main_window["message2"].Update(value=state["message2"])

            elif event == "Start":
                start_window = UI.get_start_window(main_window.current_location(), DB, "")
                main_window.close()
                while True:
                    start_event, start_values = start_window.read(timeout=10)
                    if start_event == None:
                        DB.close()
                        sys.exit()
                    elif start_event == "Back":
                        main_window = UI.get_main_window(
                            start_window.current_location(),
                            state["message1"],
                            state["message2"],
                        )
                        start_window.close()
                        break

                    elif start_event == "Start":
                        state["client_id"] = DB.getTableItemID(
                            "".join(start_values["client_listbox"]), "client"
                        )
                        state["project_id"] = DB.getTableItemID(
                            "".join(start_values["project_listbox"]), "project"
                        )
                        state["client"] = "".join(start_values["client_listbox"])
                        state["project"] = "".join(start_values["project_listbox"])
                        if state["timelogid"] > 0:
                            self.stop_timing(state, DB)
                        # Should make sure both client and project are selected before starting
                        state = self.start_timing(state, DB)
                        main_window = UI.get_main_window(
                            start_window.current_location(),
                            state["message1"],
                            state["message2"],
                        )
                        start_window.close()
                        break
                    elif start_event == "New":
                        new_window = UI.get_new_window(start_window.current_location())
                        start_window.close()
                        while True:
                            new_event, new_values = new_window.read(timeout=10)
                            if new_event == None:
                                if state["timelogid"] > 0:
                                    state = self.stop_timing(state, DB)
                                DB.close()
                                sys.exit()
                            elif new_event == "Cancel":
                                start_window = UI.get_start_window(
                                    new_window.current_location(),
                                    DB.getTableItems("client")["client_name"].tolist(),
                                    DB.getTableItems("project")["project_name"].tolist(),
                                    "",
                                )
                                new_window.close()
                                break
                            elif new_event == "Submit":
                                if new_values["new_client"] != "":
                                    if not DB.check_table_item_exists(
                                        "client", new_values["new_client"]
                                    ):
                                        DB.insert_table_item(
                                            new_values["new_client"], "client"
                                        )

                                if new_values["new_project"] != "":
                                    if not DB.check_table_item_exists(
                                        "project", new_values["new_project"]
                                    ):
                                        DB.insert_table_item(
                                            new_values["new_project"], "project"
                                        )

                                start_window = UI.get_start_window(
                                    new_window.current_location(),
                                    DB,
                                    "The items were successfully created.",
                                )
                                new_window.close()
                                break

        DB.close()

        return 0


    if __name__ == "__main__":
        run()
