import streamlit as st
import pandas as pd
import os
import sqlite3


@st.cache
def project_root():
    os.path.dirname(os.path.abspath(__file__))
    os.chdir("..")  # one directory above
    return os.path.abspath(os.curdir)


project_root = project_root()


@st.cache
def query_to_df(database=None, query=None):
    """Create a database connection to the SQLite database specified by the db_file
    Arguments:
        db_file {string} -- name of database file
    Returns:
        DataFrame -- Contents of the sql query
    """
    conn = None
    try:
        conn = sqlite3.connect(f"{project_root}/{database}.db")
    except Error as e:
        print(e)

    df = pd.read_sql_query(query, conn)
    return df


st.title("Visualizaing COVID-19 cases")

df_country_overall = query_to_df(
    database="covid_master", query="SELECT * FROM country_overall"
)

df_country_overall_top10 = df_country_overall.sort_values(
    by="confirmed", ascending=False
).iloc[:10, :]

df_country_overall_top10
