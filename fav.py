import sqlite3
import pandas as pd
import random


con = sqlite3.connect('movies.db')
cur = con.cursor()

movies = pd.read_csv('imdb_top_1000.csv')

# Rename Series_Title column
movies.rename(columns={'Series_Title': 'movie_title'}, inplace=True)


movies[['movie_title']].to_sql('Movies', con, if_exists='replace', index=True, index_label='movie_id')

# Create fav table
cur.execute('''
    CREATE TABLE IF NOT EXISTS Favorites (
        user_id INTEGER,
        movie_id INTEGER,
        PRIMARY KEY (user_id, movie_id),
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
    )
''')


# Get all user_ids and movie_ids
cur.execute('SELECT user_id FROM Users')
user_ids = [row[0] for row in cur.fetchall()]

cur.execute('SELECT movie_id FROM Movies')
movie_ids = [row[0] for row in cur.fetchall()]

favorites = []
for user_id in user_ids:
    favorite_movies = random.sample(movie_ids, k=random.randint(1, 8))
    for movie_id in favorite_movies:
        favorites.append((user_id, movie_id))

# Insert into fav table
cur.executemany('''
    INSERT INTO Favorites (user_id, movie_id)
    VALUES (?, ?)
''', favorites)


con.commit()
con.close()
