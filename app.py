import flask 
import sqlite3
import pandas as pd

app = flask.Flask(__name__)

@app.route("/")
def base():
    return flask.render_template("base.html")

@app.route("/browse")
def browse():
    return flask.render_template("browse.html")

@app.route("/search")
def search():
    return flask.render_template("search.html")

@app.route("/stats")
def stats():
    return flask.render_template("stats.html")

@app.route("/user_fav")
def user_fav():
    return flask.render_template("user_fav.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
    return flask.render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)