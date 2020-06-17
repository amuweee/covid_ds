import streamlit as st
import pandas as pd
import datetime as dt
import os
import sqlite3
import plotly.express as px
import plotly.graph_objects as go


# --------------------- Helper functions --------------------- #


@st.cache
def project_root():
    os.path.dirname(os.path.abspath(__file__))
    os.chdir(".")  # one directory above
    return os.path.abspath(os.curdir)


project_root = project_root()


@st.cache(allow_output_mutation=True)
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


def num_format(number):
    if number > 1000000:
        return f"{number/1000000:.3}M"
    elif number > 1000:
        return f"{number/1000:.3}K"
    else:
        return number

# --------------------- Loading data --------------------- #


country_overall = query_to_df(
    database="covid_master", query="SELECT * FROM country_overall"
)

country_daily = query_to_df(
    database="covid_master", query="SELECT * FROM country_daily"
)
country_daily["date"] = pd.to_datetime(country_daily["date"])

coordinates_overall = query_to_df(
    database="covid_master",
    query="SELECT latitude, longitude, confirmed FROM log_lat_overall",
)

daily_overall = query_to_df(
    database="covid_master",
    query="""
    SELECT date, sum(confirmed) confirmed, sum(death) death
    FROM country_daily
    GROUP BY date
    """
)
daily_overall["date"] = pd.to_datetime(daily_overall["date"])
daily_overall.sort_values(by="date", ascending=False, inplace=True)


# --------------------- Set up variables --------------------- #


max_date = max(country_daily["date"]).strftime("%B %d, %Y")

total_cases = country_overall["confirmed"].sum()
total_deaths = country_overall["death"].sum()
total_fatality_rate = total_deaths / total_cases

list_countries = country_overall["country"].to_list()

top_5_country = country_overall.sort_values(by="confirmed", ascending=False)


# --------------------- Dashboard --------------------- #

st.write(f"# COVID-19 Interactive Dashboard")
st.write(f"__Data as of {max_date}__")


fig = go.Figure(data=[
    go.Bar(name="Death Cases", x=daily_overall["date"], y=daily_overall["death"]),
    go.Bar(name="Confirmed Cases", x=daily_overall["date"], y=daily_overall["confirmed"])
])
fig.update_layout(barmode="stack", legend_orientation="h")
st.plotly_chart(fig)


selected_countries = st.multiselect(
    "Select the countries to display", list_countries, default=["Canada"],
)

line_chart = px.line(
    filter_country(country_daily, selected_countries),
    x="date",
    y="confirmed",
    title="Timeline of infections",
    color="country",
)
st.plotly_chart(line_chart, use_container_width=True)
