from flask import Flask, render_template

app = Flask(__name__)

@app.route("/users")
def home():
    return render_template("users.html")

if __name__ == "__main__":
    app.run(debug=True)