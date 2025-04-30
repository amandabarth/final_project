import flask 
import sqlite3
import pandas as pd
import datetime
from flask import Flask, render_template, request, redirect, url_for


app = flask.Flask(__name__)

@app.route("/browse/<user_id>")
def browse(user_id):
    movies = get_all_movies()
    return flask.render_template("browse.html", user_id=user_id, movies=movies)

def get_all_movies():
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute('''SELECT movie_id, Poster_Link, Series_Title, Released_Year, Runtime, Genre, IMDB_Rating, Overview, Director FROM Movies;''')
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

# Add helper functions for stats

def get_user_count():
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM Users")
    count = cur.fetchone()[0]
    con.close()
    return count


def get_most_common_genre(df):
    # Some rows might have multiple genres separated by commas
    all_genres = df['Genre'].dropna().str.split(', ')
    flat_genres = all_genres.explode()
    return flat_genres.value_counts().idxmax()



def get_user_movie_stats(user_id):
    con = sqlite3.connect("movies.db")
    query = '''
        SELECT M.*
        FROM Favorites F
        JOIN Movies M ON F.movie_id = M.movie_id
        WHERE F.user_id = ?
    '''
    df = pd.read_sql_query(query, con, params=(user_id,))
    con.close()
    return df

def summarize_user_movies(df):
    if df.empty:
        return None

    df['Runtime'] = df['Runtime'].str.extract(r'(\d+)').astype(float)

    # Handle genre safely
    if 'Genre' in df.columns and df['Genre'].notna().any():
        genre_series = df['Genre'].dropna().str.split(', ').explode()
        popular_genre = genre_series.value_counts().idxmax() if not genre_series.empty else 'N/A'
    else:
        popular_genre = 'N/A'

    stats_data = {
        'rating': {
            'mean': round(df['IMDB_Rating'].mean(), 2),
            'min': round(df['IMDB_Rating'].min(), 2),
            'max': round(df['IMDB_Rating'].max(), 2),
            'median': round(df['IMDB_Rating'].median(), 2),
            'std_dev': round(df['IMDB_Rating'].std(), 2)
        },
        'run_time': {
            'mean': round(df['Runtime'].mean(), 2),
            'min': round(df['Runtime'].min(), 2),
            'max': round(df['Runtime'].max(), 2),
            'median': round(df['Runtime'].median(), 2),
            'std_dev': round(df['Runtime'].std(), 2)
        },
        'fav_count': len(df),
        'popular_genre': popular_genre
    }

    return stats_data


@app.route("/user_fav/<user_id>", methods=["GET", "POST"])
def user_fav(user_id):
    favorites = get_user_fav(user_id)
    #1. get user input from form
    if flask.request.method == 'POST':
        search = flask.request.form.get("query")
        # 2. use search to get all possible movies
        movies = search_fav_movies(user_id, search)
        # 3. render template with movies as input
        return flask.render_template("user_fav.html", user_id=user_id, favorites=movies)
    return flask.render_template("user_fav.html", user_id=user_id, favorites=favorites)

def search_fav_movies(user_id, param: str):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    cur.execute(f'''SELECT Movies.movie_id, Movies.Series_Title, Movies.Overview 
                    FROM Users JOIN Favorites ON Users.user_id=Favorites.user_id JOIN Movies ON Favorites.movie_id=Movies.movie_id WHERE Users.user_id='{user_id}' AND Movies.Series_Title LIKE '%{param}%';''')
    favorites = cur.fetchall()
    con.close()
    return favorites

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

@app.route('/stats/<int:user_id>')
def stats(user_id):
    con = sqlite3.connect('movies.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Join Favorites with Movies for this user
    query = """
        SELECT M.*, F.user_id
        FROM Favorites F
        JOIN Movies M ON F.movie_id = M.movie_id
        WHERE F.user_id = ?
    """
    df = pd.read_sql_query(query, con, params=(user_id,))

    if df.empty:
        stats = {
            'rating': {'mean': 'N/A', 'min': 'N/A', 'max': 'N/A', 'median': 'N/A', 'std_dev': 'N/A'},
            'run_time': {'mean': 'N/A', 'min': 'N/A', 'max': 'N/A', 'median': 'N/A', 'std_dev': 'N/A'},
            'fav_count': 0,
            'popular_genre': 'N/A'
        }
    else:
        df['Runtime_Min'] = df['Runtime'].str.extract(r'(\d+)').astype(float)

        rating_stats = {
            'mean': round(df['IMDB_Rating'].mean(), 2),
            'min': df['IMDB_Rating'].min(),
            'max': df['IMDB_Rating'].max(),
            'median': df['IMDB_Rating'].median(),
            'std_dev': round(df['IMDB_Rating'].std(), 2)
        }

        runtime_stats = {
            'mean': round(df['Runtime_Min'].mean(), 2),
            'min': df['Runtime_Min'].min(),
            'max': df['Runtime_Min'].max(),
            'median': df['Runtime_Min'].median(),
            'std_dev': round(df['Runtime_Min'].std(), 2)
        }

        fav_count = len(df)
        df['Main_Genre'] = df['Genre'].str.split(',').str[0]
        popular_genre = df['Main_Genre'].mode()[0] if not df['Main_Genre'].mode().empty else 'N/A'

        stats = {
            'rating': rating_stats,
            'run_time': runtime_stats,
            'fav_count': fav_count,
            'popular_genre': popular_genre
        }

    con.close()
    return render_template('stats.html', stats=stats, user_id=user_id)






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
            create_new_account(username, email, password)
            return flask.render_template("login.html", error="Account Successfully Created. Please Sign in.")
    return flask.render_template("create_account.html")

def create_new_account(username, email, password):
    con = sqlite3.connect("movies.db")
    cur = con.cursor()
    signup_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(signup_date) 
    cur.execute(f'''INSERT INTO Users (username, email, password, signup_date) VALUES ('{username}', '{email}', '{password}', '{signup_date}');''')
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