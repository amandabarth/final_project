import flask 
import sqlite3
import pandas as pd

app = flask.Flask(__name__)

@app.route("/browse/<user_id>")
def browse(user_id):
    movies = get_all_movies()
    return flask.render_template("browse.html", user_id=user_id, movies=movies)

def get_all_movies():
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute('''SELECT movie_id, Poster_Link, Series_Title, Released_Year, Certificate, Runtime, Genre,IMDB_Rating, Overview, Director FROM Movies;''')
    movies = cur.fetchall()
    con.close()
    return movies

@app.route("/add_fav")
def add_fav():
    user_id = flask.request.args.get("user_id")
    movie_id = flask.request.args.get("movie_id")
    add_fav_movie(user_id, movie_id)
    return flask.redirect(flask.url_for("browse", user_id=user_id))

def add_fav_movie(user_id, movie_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''INSERT INTO Favorites (user_id, movie_id) VALUES ({user_id}, {movie_id}); ''')
    con.close()

@app.route("/search/<user_id>", methods=['GET', 'POST'])
def search(user_id):
    #1. get user input from form
    movies = []
    if flask.request.method == 'POST':
        search = flask.request.form.get("query")
        # 2. use search to get all possible movies
        movies = search_movies(search)
    # 3. render template with movies as input
    return flask.render_template("search.html", user_id=user_id, results=movies)

def search_movies(param: str):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT Poster_Link,Series_Title,Released_Year,Certificate,Runtime,Genre,IMDB_Rating,Overview,Director FROM Movies WHERE Series_Title LIKE '%{param}%' OR Overview LIKE '%{param}%';''')
    movies = cur.fetchall()
    con.close()
    return movies

@app.route("/stats/<user_id>")
def stats(user_id):
    #TODO: What is going on the stats page?
    return flask.render_template("stats.html", user_id=user_id)

@app.route("/user_fav/<user_id>")
def user_fav(user_id):
    #TODO: How to get username passed to here?
    favorites = get_user_fav(user_id)
    return flask.render_template("user_fav.html", user_id=user_id, favorites=favorites)

def get_user_fav(user_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT Movies.Poster_Link, Movies.Series_Title, Movies.Overview 
                    FROM Users JOIN Favorites ON Users.user_id=Favorites.user_id JOIN Movies ON Favorites.movie_id=Movies.movie_id WHERE Users.user_id='{user_id}';''')
    user = cur.fetchall()
    con.close()
    return user

@app.route("/", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")
        user_info = get_user(username)
        if user_info[3] == password: 
            return flask.redirect(flask.url_for("browse", user_id=user_info[0]))
        else:
            return "<p>Incorrect Username or Password. Try Again</p>"
    return flask.render_template('login.html')

def get_user(username: str):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT * FROM Users WHERE username='{username}';''')
    user = cur.fetchone()
    con.close()
    return user

if __name__ == "__main__":
    app.run(debug=True)