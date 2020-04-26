import sqlite3
import os
import constants

db_name = constants.DB_NAME

def get_root_dir():
    return os.path.dirname(os.path.abspath(__file__))


def execute_sql(command):
    # TODO: Make sure this works
    with sqlite3.connect(db_name) as conn:
        with conn.cursor as cur:
            cur.execute_sql(command)