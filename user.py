import sqlite3
from faker import Faker
from datetime import datetime
import random

# Initialize Faker library
fake = Faker()

con = sqlite3.connect('movies.db')
cur = con.cursor()

# Create users table
cur.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        signup_date TEXT NOT NULL
    )
''')

# Generate fake users
fake_users = []
for _ in range(250):
    username = fake.user_name()
    email = fake.unique.email()
    password = fake.password(length=random.randint(8, 12))
    signup_date = fake.date_time_between(start_date='-2y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
    fake_users.append((username, email, password, signup_date))

# Insert fake users
cur.executemany('''
    INSERT INTO Users (username, email, password, signup_date)
    VALUES (?, ?, ?, ?)
''', fake_users)


con.commit()
con.close()

