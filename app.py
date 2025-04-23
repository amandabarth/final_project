import flask 
import sqlite3
import pandas as pd

app = flask.Flask(__name__)

@app.route("/browse")
def browse():
    movies = get_all_movies()
    return flask.render_template("browse.html", movies=movies)
<<<<<<< HEAD

def get_all_movies():
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute('''SELECT Poster_Link,Series_Title,Released_Year,Certificate,Runtime,Genre,IMDB_Rating,Overview,Director FROM Movies;''')
    movies = cur.fetchall()
    con.close()
    return movies

=======

def get_all_movies():
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute('''SELECT 'index', Poster_Link, Series_Title, Released_Year, Certificate, Runtime, Genre,IMDB_Rating, Overview, Director FROM Movies;''')
    movies = cur.fetchall()
    con.close()
    return movies

@app.route("/add_fav/<path:user_id>/<path:movie_title>")
def add_fav(user_id, movie_title):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    #TODO: get user_id here???
    user_id = 1
    cur.execute(f'''INSERT INTO User_Fav (user_id, title) VALUES ({user_id}, {movie_title}); ''')
    con.close()
    return flask.render_template("browse.html")

>>>>>>> af7cba9e3e5d4055bff4e45713df5eead0033a4e
@app.route("/search", methods=['GET', 'POST'])
def search():
    #1. get user input from form
    if flask.request.method == 'POST':
        search = flask.request.form.get("search")
        # 2. use search to get all possible movies
        movies = search_movies(search)
    # 3. render template with movies as input
    return flask.render_template("search.html", movies=movies)

def search_movies(param: str):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT Poster_Link,Series_Title,Released_Year,Certificate,Runtime,Genre,IMDB_Rating,Overview,Director FROM Movies WHERE Series_Title LIKE '%{param}%' OR Overview LIKE '%{param}%';''')
    movies = cur.fetchall()
    con.close()
    return movies

@app.route("/stats")
def stats():
    #TODO: What is going on the stats page?
    return flask.render_template("stats.html")

<<<<<<< HEAD
@app.route("/user_fav")
def user_fav():
    #TODO: How to get username passed to here?
    return flask.render_template("user_fav.html")

def get_user_fav(username):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT Movies.Poster_Link, Movies.Series_Title FROM Users JOIN User_Fav JOIN Movies WHERE Users.username='{username}';''')
=======
@app.route("/user_fav/<path: user_id>")
def user_fav(user_id):
    #TODO: How to get username passed to here?
    favorites = get_user_fav(user_id)
    return flask.render_template("user_fav.html", favorites=favorites)

def get_user_fav(user_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT Movies.Poster_Link, Movies.Series_Title FROM Users JOIN User_Fav JOIN Movies WHERE Users.user_id='{user_id}';''')
>>>>>>> af7cba9e3e5d4055bff4e45713df5eead0033a4e
    user = cur.fetchall()
    con.close()
    return user

@app.route("/", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
        user_info = get_user(username)
        if user_info[1] == password: 
            #this is not a secure way to save a password and need user table formatting to make sure the correct info is being accessed
            return flask.render_template('browse.html')
        else:
            return "<p>Incorrect Username or Password. Try Again</p>" #we could also do flash error messages
    return flask.render_template('login.html')

def get_user(username: str):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT * FROM Users WHERE username='{username}';''')
    user = cur.fetchall()
    con.close()
    return user

if __name__ == "__main__":
    app.run(debug=True)