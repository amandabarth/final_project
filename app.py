import flask 
import sqlite3
import pandas as pd

app = flask.Flask(__name__)

@app.route("/")
def home():
    return flask.render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form.get()
        password = flask.request.form.get()
    return flask.render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)