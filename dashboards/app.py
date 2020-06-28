import streamlit as st
import pandas as pd
import datetime as dt
import os
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import pycountry
import pycountry_convert as pc

from plotly.subplots import make_subplots

import warnings

warnings.filterwarnings("ignore")


# ------------------------------------------------------------ #
# --------------------- Helper functions --------------------- #
# ------------------------------------------------------------ #


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
        If a column with country name exist in the query, then run a 

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


@st.cache(allow_output_mutation=True)
def create_country_iso_dict(df, iso):
    """Returns a ISO 3166-1 alpha-2 code for each countries based on the country name

    Args:
        df (DataFrame): data that contains a column of country names

    Returns:
        dictionary: dictionary takes country name as key, and iso code as value
    """

    c_list = df["country"].unique().tolist()
    country_iso_dict = {}
    for country in c_list:
        try:
            if iso == "iso2":
                iso_code = pycountry.countries.search_fuzzy(country)[0].alpha_2
            elif iso == "iso3":
                iso_code = pycountry.countries.search_fuzzy(country)[0].alpha_3
        except:
            iso_code = "N/A"
        country_iso_dict[country] = iso_code
    return country_iso_dict


@st.cache
def create_continent_dict(dict):

    continent_dict = {}
    codename = {
        "AS": "Asia",
        "EU": "Europe",
        "AF": "Africa",
        "NA": "North America",
        "SA": "South America",
        "OC": "Oceania",
    }
    for key, value in dict.items():
        try:
            continent = codename[pc.country_alpha2_to_continent_code(value)]
        except:
            continent = "N/A"
        continent_dict[key] = continent
    return continent_dict


def plot_daily(df, metric):
    """Plots the daily infected or death in two axis - histogram for daily, line plot for cumulative

    Args:
        df (DataFrame): contains the data to plot, requires column for data and metric
        metric (string): label of the column to plot. needs to exist in df
    """

    renames = {"confirmed": "Infections", "death": "Deaths"}
    label = renames[metric]
    df["csum"] = df[metric].cumsum()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(name="Daily", x=df["date"], y=df[metric]), secondary_y=False)
    fig.add_trace(
        go.Scatter(name="Running Total", x=df["date"], y=df["csum"]), secondary_y=True,
    )
    fig.update_layout(
        title_text=f"<b>{label} over time</b>".upper(),
        legend_orientation="h",
        width=800,
        height=500,
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=f"Daily {label}", secondary_y=False)
    fig.update_yaxes(title_text=f"Total {label}", secondary_y=True)
    st.plotly_chart(fig)


def plot_fatality(fig, df, state=False):
    """Plots the fatality over infected cases ratios over time

    Args:
        fig (plotly figure): plotly figure to chart the data onto
        df (DataFrame): data containing both infected and death cases over time
        state (bool, optional): flag for whether to chart based on state or country. Defaults to False.
    """

    if state == False:
        line_label = df["country"].iloc[0]
    else:
        line_label = df["state"].iloc[0]
    df["csum_death"] = df["death"].cumsum()
    df["csum_confirmed"] = df["confirmed"].cumsum()
    df["case_fatality_ratio"] = df["csum_death"] / df["csum_confirmed"] * 1000
    fig.add_trace(
        go.Scatter(
            x=df["date"], y=df["case_fatality_ratio"], mode="lines", name=line_label
        )
    )
    fig.update_layout(
        title_text=f"<b>Deaths per 1000 Infections</b>".upper(),
        legend_orientation="h",
        width=750,
        height=500,
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=f"Fatality Rate")


# ------------------------------------------------------------------------ #
# --------------------- Loading data into DataFrames --------------------- #
# ------------------------------------------------------------------------ #


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


# ---------------------------------------------------- #
# --------------------- Side bar --------------------- #
# ---------------------------------------------------- #


# github link and project info
st.sidebar.markdown(
    "![github](https://appcenter.ms/images/logo-github.svg)  [**PROJECT**](https://github.com/amuweee/covid_ds)"
)
st.sidebar.markdown("----")

st.sidebar.markdown("### DATA SEGMENTATION")
segmentation = st.sidebar.radio(
    label="Select data breakdown:", options=("Global", "By Countries"), index=0
)

# country and state data segmentation options
if segmentation == "By Countries":

    # order the country list to put Canada, US and UK in the first options
    ordered_list = ["Canada", "United States", "United Kingdom"]
    list_countries = country_overall["country"].to_list()
    for c in ordered_list:
        list_countries.remove(c)
    for c in list_countries:
        ordered_list.append(c)

    # create selections for countries with state level data
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

st.sidebar.markdown("----")


# ------------------------------------------------------------ #
# --------------------- Set up variables --------------------- #
# ------------------------------------------------------------ #


# date of the last data import
max_date = max(daily_overall["date"]).strftime("%B %d, %Y")

# for global cases
global_cases = country_overall["confirmed"].sum()
global_deaths = country_overall["death"].sum()
global_fataility_rate = global_deaths / global_cases

# for selections in sidebar
total_cases = df["confirmed"].sum()
total_deaths = df["death"].sum()
total_fatality_rate = total_deaths / total_cases

# dictionary for translating country name to iso codes
iso2_dict = create_country_iso_dict(country_overall, "iso2")
iso3_dict = create_country_iso_dict(country_overall, "iso3")
continent_dict = create_continent_dict(iso2_dict)


# ----------------------------------------------------- #
# --------------------- Dashboard --------------------- #
# ----------------------------------------------------- #


# headers and top leve summaries
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
st.markdown("----")
st.markdown(
    f"### **Infections: {total_cases:,} | Deaths: {total_deaths:,} | Case-Fatality Ratio: {total_fatality_rate:.2%}** "
)
if segmentation == "By Countries":
    st.markdown(
        f"#### GLOBAL **Infections: {global_cases:,} | Deaths: {global_deaths:,} | Case-Fatality Ratio: {global_fataility_rate:.2%}** "
    )

# plot daily and running total cases
plot_daily(df, "confirmed")
plot_daily(df, "death")

# plot death per infection chart
fig_line = go.Figure()
plot_fatality(fig_line, daily_overall)
if segmentation == "By Countries":
    if selection not in countries_w_states:
        plot_fatality(fig_line, df)
    else:
        if show_state:
            plot_fatality(fig_line, df, state=True)
        else:
            plot_fatality(fig_line, df)
st.plotly_chart(fig_line)

st.markdown("----")

# TODO: chroploth map - add over time filters or animation

country_overall["iso2"] = country_overall["country"].map(iso2_dict)
country_overall["iso3"] = country_overall["country"].map(iso3_dict)
country_overall["continent"] = country_overall["country"].map(continent_dict)

world_population["iso3"] = world_population["country"].map(iso3_dict)

map_data = pd.merge(country_overall, world_population, how="left", on="iso3")

map_data

global_fig = go.Figure(go.Scattergeo())
global_fig.update_geos(
    showcoastlines=True,
    coastlinecolor="Black",
    showland=True,
    showlakes=True,
    lakecolor="Lightblue",
)
global_fig.update_layout(height=600, margin={"r": 0, "l": 0, "b": 0})
st.plotly_chart(global_fig)


# scatter_geo_fig = px.choropleth(
#     country_overall,
#     locations="iso3",
#     locationmode="ISO-3",
#     color="continent",
#     projection="natural earth",
#     hover_name="country",
#     hover_data=["confirmed", "death"],
# )
# scatter_geo_fig.update_layout(
#     title_text="Global map", legend_orientation="h",
# )
# st.plotly_chart(scatter_geo_fig)

# choropleth_fig = px.choropleth(
#     title="global confirmed cases",
#     data_frame=country_overall,
#     color="confirmed",
#     color_continuous_scale="",
#     locations="iso2",
#     hover_name="country",
#     hover_data=["confirmed", "death"],
# )

# choropleth_fig.update_layout(height=400, margin={"r": 0, "l": 0, "b": 0})

# choropleth_fig.update_geos(
#     visible=False,
#     resolution=50,
#     showcountries=True,
#     countrycolor="RebeccaPurple",
#     showcoastlines=True,
#     coastlinecolor="RebeccaPurple",
# )

# st.plotly_chart(choropleth_fig)

# TODO: correlation plots: population/density/median age/urban pop
