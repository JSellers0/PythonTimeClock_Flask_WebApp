from flask import Flask, render_template, url_for

app = Flask(__name__)
app.secret_key = b';aeirja_)(_9u-a9jdfae90ej-e09!@aldjfa;'

@app.route("/webtime", methods=["GET", "PUT"])
def webtime():
    return render_template("webtime.html")

@app.route("/users")
def users():
    return render_template("users.html")

@app.route("/webtime/start", methods=["POST", "GET"])
def start():
    return render_template("start.html")

@app.route("/webtime/new", methods=["POST", "GET"])
def new():
    return render_template("new.html")

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

@app.route("/webtime/register")
def register():
    return "Register"

@app.route("/webtime/login")
def login():
    return "Log In"

@app.route("/webtime/logout")
def logout():
    return "Log Out"

if __name__ == "__main__":
    app.run(debug=True)