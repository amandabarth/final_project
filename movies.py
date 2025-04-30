import pandas as pd
import sqlite3

# Load CSV and write to DB
df_movies = pd.read_csv('imdb_top_1000.csv')
con = sqlite3.connect('movies.db')
df_movies.to_sql('Movies', con, if_exists='replace', index=True, index_label='movie_id')

# Clean data by removing rows with NULLs in important columns
cur = con.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS Movies_cleaned (
    movie_id INTEGER PRIMARY KEY,
    Poster_Link TEXT,
    Series_Title TEXT,
    Released_Year TEXT,
    Runtime TEXT,
    Genre TEXT,
    IMDB_Rating REAL,
    Overview TEXT,
    Director TEXT,
    Star1 TEXT,
    Star2 TEXT,
    Star3 TEXT,
    Star4 TEXT
);

INSERT INTO Movies_cleaned (
    movie_id, Poster_Link, Series_Title, Released_Year,
    Runtime, Genre, IMDB_Rating, Overview, Director,
    Star1, Star2, Star3, Star4
)
SELECT
    movie_id, Poster_Link, Series_Title, Released_Year,
    Runtime, Genre, IMDB_Rating, Overview, Director,
    Star1, Star2, Star3, Star4
FROM Movies
WHERE
    Poster_Link IS NOT NULL AND
    Series_Title IS NOT NULL AND
    Released_Year IS NOT NULL AND
    Runtime IS NOT NULL AND
    Genre IS NOT NULL AND
    IMDB_Rating IS NOT NULL AND
    Overview IS NOT NULL AND
    Director IS NOT NULL AND
    Star1 IS NOT NULL AND
    Star2 IS NOT NULL AND
    Star3 IS NOT NULL AND
    Star4 IS NOT NULL;

DROP TABLE Movies;
ALTER TABLE Movies_cleaned RENAME TO Movies;
""")

con.commit()
con.close()

print("Data cleaned and saved to movies.db.")
