class CovidConfigs:

    # source data
    DF_NAME_URL_DICT = {
        "confirmed_global": "https://raw.githubusercontent.com/cssegisanddata/covid-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
        "confirmed_usa": "https://raw.githubusercontent.com/cssegisanddata/covid-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv",
        "death_global": "https://raw.githubusercontent.com/cssegisanddata/covid-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
        "death_usa": "https://raw.githubusercontent.com/cssegisanddata/covid-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv",
    }

    # renaming column names
    LOCATION_COLUMN_DICT = {
        "Province_State": "state",
        "Country_Region": "country",
        "Province/State": "state",
        "Country/Region": "country",
        "Lat": "latitude",
        "Long_": "longitude",
        "Long": "longitude",
    }
    LOCATION_COLUMNS = ["country", "state", "latitude", "longitude"]
    DROP_COLUMNS = [
        "UID",
        "iso2",
        "iso3",
        "code3",
        "FIPS",
        "Admin2",
        "Combined_Key",
        "Population",
    ]

    # csv payload name
    CSV_NAME = "covid_daily_data.csv"

    # SQL properties
    SETUP_SQL_SCRIPT = "setup_covid_daily"
