import flask 
import sqlite3
import pandas as pd
import datetime

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
    movies = get_all_movies()
    if add_fav_movie(user_id, movie_id): 
        return flask.render_template("browse.html", user_id=user_id,movies=movies, update="New Favorite Movie Added")
    return flask.render_template("browse.html", user_id=user_id,movies=movies, update="Movie Already Saved to Favorites")

def add_fav_movie(user_id, movie_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT * FROM Favorites WHERE EXISTS(SELECT * FROM Favorites WHERE user_id={user_id} AND movie_id={movie_id});''')
    exists = cur.fetchall()
    print(exists)
    if len(exists) >= 1:
        con.close()
        return False
    cur.execute(f'''INSERT INTO Favorites (user_id, movie_id) VALUES ({user_id}, {movie_id}); ''')
    con.commit()
    con.close()
    return True

@app.route("/remove_fav")
def remove_fav():
    user_id = flask.request.args.get("user_id")
    movie_id = flask.request.args.get("movie_id")
    remove_fav_movie(user_id, movie_id)
    movies = get_user_fav(user_id)
    return flask.render_template("user_fav.html", user_id=user_id, favorites=movies, update="Favorite Movie Removed")

def remove_fav_movie(user_id, movie_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''DELETE FROM Favorites WHERE user_id={user_id} AND movie_id={movie_id}; ''')
    con.commit()
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
    cur.execute(f'''SELECT movie_id,Series_Title,Released_Year,Certificate,Runtime,Genre,IMDB_Rating,Overview,Director FROM Movies WHERE Series_Title LIKE '%{param}%' OR Overview LIKE '% {param} %';''')
    movies = cur.fetchall()
    con.close()
    return movies

@app.route("/stats/<user_id>")
def stats(user_id):
    #TODO: What is going on the stats page?
    return flask.render_template("stats.html", user_id=user_id)

@app.route("/user_fav/<user_id>")
def user_fav(user_id):
    favorites = get_user_fav(user_id)
    return flask.render_template("user_fav.html", user_id=user_id, favorites=favorites)

def get_user_fav(user_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT Movies.movie_id, Movies.Series_Title, Movies.Overview 
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
        if user_info and user_info[3] == password : 
            return flask.redirect(flask.url_for("browse", user_id=user_info[0]))
        else:
            return flask.render_template("login.html", error="Incorrect Username or Password. Try Again")
    return flask.render_template('login.html')

def get_user(username: str):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT * FROM Users WHERE username='{username}';''')
    user = cur.fetchone()
    con.close()
    return user


@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    if flask.request.method == 'POST':
        username = flask.request.form.get("username")
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
        confirm_password = flask.request.form.get("confirm_password")
        if password != confirm_password:
            return flask.render_template("create_account.html", error="TRY AGAIN. Passwords do not match")
        else:
            user_id = create_new_account(username, password, confirm_password)
            return flask.redirect(flask.url_for("login"))
    return flask.render_template("create_account.html")

def create_new_account(username, email, password, confirm_password):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    signup_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(signup_date) 
    cur.execute(f'''INSERT INTO Users (username, email, password, signup_date) VALUES ({username}, {email}, {password}, {signup_date});''')
    con.commit()
    con.close()

@app.route("/user_info/<user_id>", methods=['GET', 'POST'])
def user_info(user_id):
    #TODO: Show user info and allow them to change password and delete account
    user_info = get_user_info(user_id)
    if flask.request.method == 'POST':
        if flask.request.form.get("remove") == "remove":
            remove_user(user_id)
            return flask.render_template("login.html", error="Account Successfully Removed")
        elif flask.request.form.get("update_password") == "update_password":
            current_password = flask.request.form.get("current_password")
            new_password = flask.request.form.get("new_password")
            confirm_new_password = flask.request.form.get("confirm_new_password")
            if user_info[3] == current_password and new_password == confirm_new_password:
                update_password(user_id, new_password)
                return flask.render_template('user_info.html', user_id=user_id, user_info=user_info, error='Password Reset Successfully')
            else:
                return flask.render_template('user_info.html', user_id=user_id, user_info=user_info ,error='Passwords did not match. Try Again.')

    return flask.render_template('user_info.html', user_id=user_id, user_info=user_info)

def get_user_info(user_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT * FROM Users WHERE user_id={user_id};''')
    user = cur.fetchone()
    con.close()
    return user

def update_password(user_id, new_password):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''UPDATE Users SET password='{new_password}' WHERE user_id={user_id};''')
    con.commit()
    con.close()

def remove_user(user_id):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''DELETE FROM Users WHERE user_id={user_id};''')
    con.commit()
    con.close()
    

if __name__ == "__main__":
    app.run(debug=True)