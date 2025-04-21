import pandas as pd
import sqlite3

con = sqlite3.connect('movies.db')

cur = con.cursor()

df_movies = pd.read_csv('imdb_top_1000.csv')
df_movies.to_sql('Movies', con, if_exists='replace', index=True)

con.close()