class ETLConfigs:

    # source data
    DF_NAME_URL_DICT = {
        "confirmed_global": "https://raw.githubusercontent.com/cssegisanddata/covid-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
        "confirmed_usa": "https://raw.githubusercontent.com/cssegisanddata/covid-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv",
        "death_global": "https://raw.githubusercontent.com/cssegisanddata/covid-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
        "death_usa": "https://raw.githubusercontent.com/cssegisanddata/covid-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv",
        "recovered_global": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv",
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

    # SQL properties
    DB_NAME = "covid_master"
    TABLE_NAME = "covid_daily"
    SETUP_SQL_SCRIPT = "setup_table"
    SWAP_SQL_SCRIPT = "swap_table"
    SQL_DTYPES = {
        "country": "TEXT",
        "state": "TEXT",
        "latitude": "REAL",
        "longitude": "REAL",
        "date": "TEXT",
        "confirmed": "INTEGER",
        "death": "INTEGER",
        "etl_load_time": "TEXT",
    }


class WorldPopConfig:

    # source data
    POP_URL = "https://www.worldometers.info/world-population/population-by-country/"

    # DataFrame properties
    HEADER_DICT = {
        "#": "id",
        "Country (or dependency)": "country",
        "Population (2020)": "population_2020",
        "Yearly Change": "yoy_delta_perc",
        "Net Change": "yoy_delta_amt",
        "Density (P/Km²)": "density_km2",
        "Land Area (Km²)": "land_km2",
        "Migrants (net)": "net_migrants",
        "Fert. Rate": "fertility_rate",
        "Med. Age": "median_age",
        "Urban Pop %": "urban_pop_perc",
        "World Share": "population_world_share",
    }

    # SQL properties
    DB_NAME = "population"
    TABLE_NAME = "world_population"
    SETUP_SQL = f"DROP TABLE IF EXISTS {TABLE_NAME}"
    SQL_DTYPES = {
        "id": "INTEGER",
        "country": "TEXT",
        "population_2020": "INTEGER",
        "yoy_delta_perc": "TEXT",
        "yay_delta_amt": "INTEGER",
        "density_km2": "INTEGER",
        "land_km2": "INTEGER",
        "net_migrants": "INTEGER",
        "fertility_rate": "REAL",
        "median_age": "INTEGER",
        "urban_pop_perc": "TEXT",
        "population_world_share": "TEXT",
    }


class DBViewConfig:

    DB_NAME = ETLConfigs.DB_NAME
    SQL_SCRIPT = "create_views"
