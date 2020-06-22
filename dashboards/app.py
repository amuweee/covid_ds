import streamlit as st
import pandas as pd
import datetime as dt
import os
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots

import warnings

warnings.filterwarnings("ignore")

# --------------------- Helper functions --------------------- #


@st.cache
def project_root():
    """Get the path to the project root

    Returns:
        string: path to the project root
    """
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


def plot_daily(df, metric):

    renames = {"confirmed": "Infections", "death": "Deaths"}
    label = renames[metric]
    df["csum"] = df[metric].cumsum()
    country = df["country"].iloc[0]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(name="Daily", x=df["date"], y=df[metric]), secondary_y=False)
    fig.add_trace(
        go.Scatter(name="Running Total", x=df["date"], y=df["csum"]), secondary_y=True,
    )
    fig.update_layout(
        title_text=f"<b>{label} over time</b>".upper(), legend_orientation="h",
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=f"Daily {label}", secondary_y=False)
    fig.update_yaxes(title_text=f"Total {label}", secondary_y=True)
    st.plotly_chart(fig)


# --------------------- Loading data --------------------- #


country_overall = query_to_df(
    database="covid_master", query="SELECT * FROM country_overall"
)

country_daily = query_to_df(
    database="covid_master", query="SELECT * FROM country_daily"
)
country_daily["date"] = pd.to_datetime(country_daily["date"])

state_daily = query_to_df(
    database="covid_master", query="SELECT * FROM state_daily WHERE state IS NOT NULL"
)

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

world_population = query_to_df(
    database="population", query="SELECT * FROM world_population"
)

countries_w_states = state_daily["country"].unique().tolist()


# --------------------- Side bar --------------------- #

st.sidebar.markdown("### DATA SEGMENTATION")
segmentation = st.sidebar.radio(
    label="Select data breakdown:", options=("Global", "By Countries"), index=0
)

if segmentation == "By Countries":

    ordered_list = ["Canada", "United States", "United Kingdom"]
    list_countries = country_overall["country"].to_list()

    for c in ordered_list:
        list_countries.remove(c)
    for c in list_countries:
        ordered_list.append(c)

    selection = st.sidebar.selectbox(
        label="Select the countries to display", options=ordered_list,
    )
    df = country_daily[country_daily["country"] == selection]

    if selection in countries_w_states:
        show_state = st.sidebar.checkbox("Breakdown by state/province")

        if show_state:
            df_selection = state_daily[state_daily["country"] == selection]
            state_list = df_selection["state"].unique().tolist()

            state = st.sidebar.selectbox(
                label="Select the state to display", options=state_list
            )

            df = state_daily[state_daily["state"] == state]

elif segmentation == "Global":
    df = daily_overall
    df["country"] = "Global"


# --------------------- Set up variables --------------------- #


max_date = max(daily_overall["date"]).strftime("%B %d, %Y")

# for global cases
global_cases = country_overall["confirmed"].sum()
global_deaths = country_overall["death"].sum()
global_fataility_rate = global_deaths / global_cases

# for selections in sidebar
total_cases = df["confirmed"].sum()
total_deaths = df["death"].sum()
total_fatality_rate = total_deaths / total_cases

top_5_country = country_overall.sort_values(by="confirmed", ascending=False)


# --------------------- Dashboard --------------------- #

st.write("# COVID-19 Interactive Dashboard")
st.write(f"__Data as of {max_date}__")
st.markdown(
    """
    COVID-19 related data is collected from [JHU CSSE](https://github.com/CSSEGISandData/COVID-19)  
    World population date us collected from [Worldometer](https://www.worldometers.info/world-population/population-by-country/)  
    **Confirmed Infection** cases include presumptive or probable cases  
    **Case-Fatality Ratio** = Recorded Deaths / Confirmed Infections
    """
)
st.markdown(
    f"### **Infections: {total_cases:,} | Deaths: {total_deaths:,} | Case-Fatality Ratio: {total_fatality_rate:.2%}** "
)
if segmentation == "By Countries":
    st.markdown(
        f"#### GLOBAL **Infections: {global_cases:,} | Deaths: {global_deaths:,} | Case-Fatality Ratio: {global_fataility_rate:.2%}** "
    )

plot_daily(df, "confirmed")
plot_daily(df, "death")


# Infected charts
# confirmed_fig = make_subplots(specs=[[{"secondary_y": True}]])
# confirmed_fig.add_trace(
#     go.Bar(name="Daily", x=df["date"], y=df["confirmed"]), secondary_y=False
# )
# confirmed_fig.add_trace(
#     go.Scatter(name="Running Total", x=df["date"], y=df["csum_confirmed"]),
#     secondary_y=True,
# )
# confirmed_fig.update_layout(
#     title_text="Confirmed Infections over time", legend_orientation="h"
# )
# confirmed_fig.update_xaxes(title_text="Date")
# confirmed_fig.update_yaxes(title_text="<b>Daily Infections</b>", secondary_y=False)
# confirmed_fig.update_yaxes(title_text="<b>Total Infections</b>", secondary_y=True)
# st.plotly_chart(confirmed_fig)


# # Death charts
# death_fig = make_subplots(specs=[[{"secondary_y": True}]])
# death_fig.add_trace(
#     go.Bar(name="Daily", x=df["date"], y=df["death"]), secondary_y=False
# )
# death_fig.add_trace(
#     go.Scatter(name="Running Total", x=df["date"], y=df["csum_death"]),
#     secondary_y=True,
# )
# death_fig.update_layout(title_text="Death over time", legend_orientation="h")
# death_fig.update_xaxes(title_text="Date")
# death_fig.update_yaxes(title_text="<b>Daily Deaths</b>", secondary_y=False)
# death_fig.update_yaxes(title_text="<b>Total Deaths</b>", secondary_y=True)
# st.plotly_chart(death_fig)


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
