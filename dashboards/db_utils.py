import pandas as pd
import sqlite3
import os


def project_root():
    os.path.abspath(os.curdir)
    os.chdir(".")  # one directory above
    return os.path.abspath(os.curdir)


class CovidDBQuery:
    def __init__(self):
        self.database = "covid_master.db"
        self.conn = sqlite3.connect(f"{project_root()}/{self.database}")

    def query_to_df(self, query):
        """Create a database connection to the SQLite database specified by the db_file
        Arguments:
            db_file {string} -- name of database file
        Returns:
            DataFrame -- Contents of the sql query
        """
        df = pd.read_sql_query(query, self.conn)
        return df
