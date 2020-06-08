import streamlit as st
import pandas as pd
import datetime as dt
import os
import sqlite3
import plotly.express as px


@st.cache
def project_root():
    os.path.dirname(os.path.abspath(__file__))
    os.chdir(".")  # one directory above
    return os.path.abspath(os.curdir)


project_root = project_root()


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


def filter_country(df, country):

    return df[df["country"].isin(country)]


# loading data
country_overall = query_to_df(
    database="covid_master", query="SELECT * FROM country_overall"
)

country_daily = query_to_df(
    database="covid_master", query="SELECT * FROM country_daily"
)
country_daily["date"] = pd.to_datetime(country_daily["date"])

coordinates_overall = query_to_df(
    database="covid_master",
    query="SELECT latitude as lat, longitude as lon, confirmed FROM log_lat_overall",
)

# setup variables
max_date = max(country_daily["date"])


# sidebars
list_countries = country_overall["country"].to_list()
selected_countries = st.sidebar.multiselect(
    "Select the countries to display",
    list_countries,
    default=["US", "Brazil", "Russia", "Spain", "United Kingdom", "China"],
)

# TODO: add slider
# st.sidebar.slider(
#     "Select date ranges",
#     min_value=min_date,
#     max_value=max_date,
#     value="2020-51-01",
#     step=1,
# )

"""
# COVID-19 Dashboard
- **asd**  
- _mnd_  
"""

max_date

line_chart = px.line(
    filter_country(country_daily, selected_countries),
    x="date",
    y="confirmed",
    title="Timeline of infections",
    color="country",
)
st.plotly_chart(line_chart, use_container_width=True)
