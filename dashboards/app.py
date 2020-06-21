import streamlit as st
import pandas as pd
import datetime as dt
import os
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots

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
    """,
)
daily_overall["date"] = pd.to_datetime(daily_overall["date"])


# --------------------- Side bar --------------------- #

st.sidebar.markdown("### DATA SEGMENTATION")
segmentation = st.sidebar.radio(
    label="Select data breakdown:", options=("Global", "By Countries"), index=0
)

if segmentation == "By Countries":
    list_countries = country_overall["country"].to_list()
    selected_countries = st.sidebar.multiselect(
        "Select the countries to display", list_countries, default=["US"],
    )
    df = country_daily[country_daily["country"].isin(selected_countries)]
elif segmentation == "Global":
    df = daily_overall
    df["country"] = "Global"


# --------------------- Set up variables --------------------- #


max_date = max(df["date"]).strftime("%B %d, %Y")

total_cases = df["confirmed"].sum()
total_deaths = df["death"].sum()
total_fatality_rate = total_deaths / total_cases

# df["csum_confirmed"] = df.groupby(by="date")["confirmed"].cumsum()
# df["csum_death"] = df.groupby(by="date")["death"].cumsum()
df_g = df.groupby(by="date")
df_g.cumsum()


top_5_country = country_overall.sort_values(by="confirmed", ascending=False)


# --------------------- Dashboard --------------------- #

st.write("# COVID-19 Interactive Dashboard")
st.write(f"__Data as of {max_date}__")
st.markdown(
    f"### **Infections: {total_cases:,} - Deaths: {total_deaths:,} - Fatality Rate: {(total_deaths/total_cases):.2%}** "
)


# Infected charts
confirmed_fig = make_subplots(specs=[[{"secondary_y": True}]])
confirmed_fig.add_trace(
    go.Bar(name="Daily", x=df["date"], y=df["confirmed"]), secondary_y=False
)
confirmed_fig.add_trace(
    go.Scatter(name="Running Total", x=df["date"], y=df["csum_confirmed"]),
    secondary_y=True,
)
confirmed_fig.update_layout(
    title_text="Confirmed Infections over time", legend_orientation="h"
)
confirmed_fig.update_xaxes(title_text="Date")
confirmed_fig.update_yaxes(title_text="<b>Daily Infections</b>", secondary_y=False)
confirmed_fig.update_yaxes(title_text="<b>Total Infections</b>", secondary_y=True)
st.plotly_chart(confirmed_fig)


# Death charts
death_fig = make_subplots(specs=[[{"secondary_y": True}]])
death_fig.add_trace(
    go.Bar(name="Daily", x=df["date"], y=df["death"]), secondary_y=False
)
death_fig.add_trace(
    go.Scatter(name="Running Total", x=df["date"], y=df["csum_death"]),
    secondary_y=True,
)
death_fig.update_layout(title_text="Death over time", legend_orientation="h")
death_fig.update_xaxes(title_text="Date")
death_fig.update_yaxes(title_text="<b>Daily Deaths</b>", secondary_y=False)
death_fig.update_yaxes(title_text="<b>Total Deaths</b>", secondary_y=True)
st.plotly_chart(death_fig)


# fig_daily = go.Figure(
# data=[
# go.Bar(name="Death Cases", x=daily_overall["date"], y=daily_overall["death"]),
# go.Bar(
# name="Confirmed Cases",
# x=daily_overall["date"],
# y=daily_overall["confirmed"],
# ),
# ]
# )
# fig_daily.update_layout(barmode="relative", legend_orientation="h")
# st.plotly_chart(fig_daily)


# line_chart = px.line(
#     filter_country(country_daily, selected_countries),
#     x="date",
#     y="confirmed",
#     title="Timeline of infections",
#     color="country",
# )
# st.plotly_chart(line_chart, use_container_width=True)
