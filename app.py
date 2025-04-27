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
    cur.execute('''SELECT 'index', Poster_Link, Series_Title, Released_Year, Certificate, Runtime, Genre,IMDB_Rating, Overview, Director FROM Movies;''')
    movies = cur.fetchall()
    con.close()
    return movies

@app.route("/add_fav")
def add_fav():
    user_id = flask.request.args.get("user_id")
    movie_id = flask.request.args.get("movie_id")
    movie_title = flask.request.args.get("movie_title")
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    #TODO: format user_fav table types
    cur.execute(f'''INSERT INTO Favorites (user_id, movie_id) VALUES ({user_id}, {movie_id}); ''')
    con.close()
    return flask.render_template("browse.html", user_id=user_id)

@app.route("/search", methods=['GET', 'POST'])
def search():
    #1. get user input from form
    movies = []
    if flask.request.method == 'POST':
        search = flask.request.form.get("query")
        # 2. use search to get all possible movies
        movies = search_movies(search)
    # 3. render template with movies as input
    return flask.render_template("search.html", results=movies)

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

@app.route("/user_fav/<user_id>")
def user_fav(user_id):
    #TODO: How to get username passed to here?
    favorites = get_user_fav(user_id)
    return flask.render_template("user_fav.html", user_id=user_id, favorites=favorites)

def get_user_fav(user_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT Movies.Poster_Link, Movies.Series_Title, Movies.Overview 
                    FROM Users JOIN Favorites ON Users.user_id=Favorites.user_id JOIN Movies ON Favorites.movie_id=Movies.'index' WHERE Users.user_id='{user_id}';''')
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
            return "<p>Incorrect Username or Password. Try Again</p>" #we could also do flash error messages
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