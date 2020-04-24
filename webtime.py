from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/users")
def users():
    return render_template("users.html")

@app.route("/webtime", methods=["POST", "GET"])
def webtime():
    form = MainForm()
    if form.start.data:
        return redirect(url_for("start"))
    elif form.stop.data:
        # Stop updates to main
        flash("Stopped Timing.")
        return render_template("main.html", form=form)
    elif form.adjust.data:
        return redirect(url_for("adjust"))
    elif form.report.data:
        return redirect(url_for("report"))
    if request.args.get('message'):
        message = request.args.get('message')
    else:
        message = "Welcome to Python TimeClock.  Click Start to start timing."
    return render_template("webtime.html", form=form, message=message)

@app.route("/webtime/start", methods=["POST", "GET"])
def start():
    form = StartForm()
    form.client_list.choices = [(name, name) for name in db.getTableItems("client").sort_values(by="clientID")["client_name"].tolist()]
    form.project_list.choices = [(name, name) for name in db.getTableItems("project").sort_values(by="projectID")["project_name"].tolist()]
    print(form.validate_on_submit())
    if form.validate_on_submit():
        # ToDo: Replace Flash messages with DB check for current timelog row
        flash("Started timing {} - {} at {}".format("client", "project", "timestamp"))
        return redirect(url_for("main"))
    return render_template("start.html", form=form)

@app.route("/webtime/new", methods=["POST", "GET"])
def new():
    form = NewForm()
    # Replace with validations that entries don't already exist
    if form.submit.data:
        print(form.submit.data)
        message = ""
        if form.new_client.data:
            db.create_table_item(form.new_client.data, "client")
            message += "{} added to client ".format(form.new_client.data)
        if form.new_project.data:
            db.create_table_item(form.new_project.data, "project")
            message += "{} added to project".format(form.new_project.data)
        flash(message)
        return redirect(url_for("start"))
    return render_template("new.html", form=form)

@app.route("/webtime/adjust")
def adjust():
    return render_template("adjust.html")

@app.route("/webtime/adjust/time")
def adjust_time():
    return render_template("adjust_time.html")

@app.route("/webtime/adjust/client")
def adjust_client():
    return render_template("adjust_client.html")

@app.route("/webtime/adjust/project")
def adjust_project():
    return render_template("adjust_project.html")

@app.route("/webtime/report")
def report():
    return render_template("report.html")

if __name__ == "__main__":
    app.run(debug=True)