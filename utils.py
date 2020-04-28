import os
import datetime as dt
import sqlite3

from etl.constants import ETLConfigs, WorldPopConfig

def project_root():
    return os.path.dirname(os.path.abspath(__file__))


class DBUpdates:
    """Class for wrapping all the scripte related to updating the SQLite3 database
    """
    def __init__(self):
        """Setting all constants and props required to run SQL commands
        """

        # Static properties
        self.project_root = project_root()
        self.database_name = ETLConfigs.DB_NAME
        self.table_name = ETLConfigs.TABLE_NAME
        self.setup_command = ETLConfigs.SETUP_SQL_SCRIPT
        self.swap_command = ETLConfigs.SWAP_SQL_SCRIPT
        self.sql_dtypes = ETLConfigs.SQL_DTYPES

        # SQL scripts
        with open(
            "{}/sql/{}.sql".format(self.project_root, self.setup_command)
        ) as setup_sql:
            self.setup_sql_command = setup_sql.read()
        with open(
            "{}/sql/{}.sql".format(self.project_root, self.swap_command)
        ) as swap_sql:
            self.swap_sql_command = swap_sql.read()

        # Create/establish DB connection
        self.conn = sqlite3.connect(
            "{}/{}.db".format(self.project_root, self.database_name)
        )
        self.cur = self.conn.cursor()

    def create_table(self):

        self.cur.execute(self.setup_sql_command)
        self.conn.commit()

    def insert_to_table(self, df):
        
        df.to_sql(
            name="covid_daily_new",
            con=self.conn,
            dtype=self.sql_dtypes,
            if_exists="replace",
            index=False
        )

    def swap_tables(self):

        self.cur.executescript(self.swap_sql_command)
        self.conn.commit()
        self.cur.close()
        self.conn.close()


class WorldPopUpdates:

    def __init__(self):
        # Static properties
        self.project_root = project_root()
        self.database_name = WorldPopConfig.DB_NAME
        self.table_name = WorldPopConfig.TABLE_NAME
        self.setup_sql_command = WorldPopConfig.SETUP_SQL
        self.sql_dtypes = WorldPopConfig.SQL_DTYPES

        # Create/establish DB connection
        self.conn = sqlite3.connect(
            "{}/{}.db".format(self.project_root, self.database_name)
        )
        self.cur = self.conn.cursor()

    def drop_existing_table(self):

        self.cur.execute(self.setup_sql_command)
        self.conn.commit()

    def create_insert_table(self, df):
        
        df.to_sql(
            name=self.table_name,
            con=self.conn,
            dtype=self.sql_dtypes,
            if_exists="replace",
            index=False
        )
        self.conn.commit()
        self.cur.close()
        self.conn.close()