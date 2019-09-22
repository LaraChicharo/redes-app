import sqlite3

DATABASE_NAME = '../db/database.db'

def create_user(username, password):
    db_connection = sqlite3.connect(DATABASE_NAME)
    c = db_connection.cursor()
    operation = 'INSERT INTO user (username, password) VALUES (?, ?)'
    values = (username, password)
    c.execute(operation, values)
    db_connection.commit()
    db_connection.close()

def check_user_pass(username, password):
    db_connection = sqlite3.connect(DATABASE_NAME)
    c = db_connection.cursor()
    operation = 'SELECT * FROM user WHERE username=? and password=?'
    values = (username, password)
    c.execute(operation, values)
    res = c.fetchone()
    db_connection.close()
    return res

