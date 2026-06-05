import sqlite3
#DATABASE_NAME = 'database.db'

#def get_db_connection():
#     conn = sqlite3.connect(DATABASE_NAME)
#     conn.row_factory = sqlite3.Row
#     return conn

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance/database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn