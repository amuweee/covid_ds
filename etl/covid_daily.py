import datetime as dt
import numpy as np
import pandas as pd
import requests
import csv
from io import StringIO
pd.options.mode.chained_assignment = None

from etl.constants import ETLConfigs
from utils import DBUpdates


class CovidPipeline:
    """
    Class for handling tasks associated with retrieving, transforming to database setup, and writing to redshift

    Uses Pandas dataframe object as intermediate storage and transfer mechanism.
    >>> covid_daily = CovidDailyData()
    >>> payload = covid_daily.body
    >>> type(payload)
    pandas.core.frame.DataFrame

    Interfaces & Services
    ---------------------
    aws (Default: AWSInterface) - Provides access and methods to both AWS Redshift and AWS S3. Wrapper class
    for RedshiftInterface and S3Interface.

    State Control
    -------------
    Utilizes basic state flow control to prevent invalid transitions that may cause issues with the data.
    E.g. Once instance body has been transformed, it cannot be sent through the transform process
    again.
    # TODO: Add docstring here
    Pipeline
    --------
    1. Setup
    2. Extract
    3. Transform
    4. Load
    5. Teardown

    """

    def __init__(self, dbupdates=DBUpdates()):
        # Payload and sql interface
        self.database = dbupdates
        self.body = pd.DataFrame()

        # String properties
        self.df_names_url_dict = ETLConfigs.DF_NAME_URL_DICT
        self.drop_columns = ETLConfigs.DROP_COLUMNS
        self.location_column_dict = ETLConfigs.LOCATION_COLUMN_DICT
        self.locations = ETLConfigs.LOCATION_COLUMNS

    def download_to_df(self, url):
        """Given an url to a hosted csv file, download and stores as DataFrame
        Arguments:
            url {string} -- url of the gitrepo that host the csv file
        Returns:
            DataFrame -- contents of the csv stored in a DataFrame object
        """
        with requests.Session() as s:
            download = s.get(url)
            decoded_content = download.content.decode("utf-8")
            csv_data = StringIO(decoded_content)
            df = pd.read_csv(csv_data, delimiter=",")
        return df

    def format_date(self, original_date):
        """Turns a MM/DD/YY date format into YYYY/MM/DD format
        Arguments:
            original_date {string} -- date in MM/DD/YY format
        Returns:
            string -- date in YYYY/MM/DD format
        """
        renamed_date = dt.datetime.strptime(original_date, "%m/%d/%y")
        return renamed_date

    def calculate_daily_delta(self, df, category):
        """Takes the raw download from the gitrepo csv files then does three things:
                Drop the US sepcific columns and rename the rest to standardize
                Reformat the dates with format_date() method and calculate the daily variance
                Unpivot pd.melt() the date columns so that the measures are are all under one date column
        Arguments:
            df {DataFrame} -- downloaded csv from gitrepo
            category {string} -- category of the csv (confirmed or deaths)
        Returns:
            DataFrame -- DataFrame is in the resulting format ready for db insert
        """

        # drop extra columns existing uniquely in the US specific data
        df.drop(columns=self.drop_columns, inplace=True, errors="ignore")
        # rename columns to standardize
        df.rename(columns=self.location_column_dict, inplace=True, errors="ignore")
        # set column lists
        all_columns = list(df.columns.values)
        dates = [i for i in all_columns if i not in self.locations]
        # create target payload
        df_locations = df[self.locations]
        df_dates = df[dates]
        # replace dates to datetime format and calculate daily cases (rather than cumulative)
        for i in range(len(df_dates.columns)):
            # except for the first date as it is a starting point
            # only date formatting is performed
            if i == 0:
                df_dates.rename(
                    columns={
                        df_dates.columns[0]: self.format_date(df_dates.columns[0])
                    },
                    inplace=True,
                )
            # other columns will be a difference between adjascent days
            # a new column is created as well as date formatting
            else:
                df_dates["{}".format(self.format_date(df_dates.columns[i]))] = (
                    df_dates.iloc[:, i] - df_dates.iloc[:, (i - 1)]
                )
        # remove the old date columns
        df_dates.drop(columns=dates, inplace=True, errors="ignore")
        # put it all together
        df_merged = df_locations.merge(
            df_dates, how="outer", left_index=True, right_index=True
        )
        # melt(unpivot) the date columns so that they are all under one column
        dates = [i for i in df_merged.columns if i not in self.locations]
        df_melt = pd.melt(
            df_merged,
            id_vars=self.locations,
            value_vars=dates,
            var_name="date",
            value_name=category,
        )
        return df_melt

    def setup(self):
        """Executes setup SQL command to prepare database for the storage of Covid-19 daily data.
        Method can only be used if working with new instance of CoviddailyConfig object in NEW state, or an instance
        of an object that has completed processing and in a POST TEAR DOWN state
        """
        self.database.create_table()

    def extract(self):
        """Executes the source query for daily covid report data where 
        """

        self.df_confirmed_global = self.download_to_df(
            self.df_names_url_dict["confirmed_global"]
        )
        self.df_confirmed_usa = self.download_to_df(
            self.df_names_url_dict["confirmed_usa"]
        )
        self.df_death_global = self.download_to_df(
            self.df_names_url_dict["death_global"]
        )
        self.df_death_usa = self.download_to_df(self.df_names_url_dict["death_usa"])

    def transform(self):

        # transform date fields, and calculate the daily deltas
        self.df_confirmed_global = self.calculate_daily_delta(
            self.df_confirmed_global, "confirmed"
        )
        self.df_confirmed_usa = self.calculate_daily_delta(
            self.df_confirmed_usa, "confirmed"
        )
        self.df_death_global = self.calculate_daily_delta(self.df_death_global, "death")
        self.df_death_usa = self.calculate_daily_delta(self.df_death_usa, "death")

        # join the confirmed and deaths figures by global and USA
        self.global_all = self.df_confirmed_global.join(
            self.df_death_global["death"], how="left"
        )
        self.usa_all = self.df_confirmed_usa.join(
            self.df_death_usa["death"], how="left"
        )

        # concatenate everything together as the payload upload
        self.body = pd.concat([self.global_all, self.usa_all])

        # the global dataset contains a daily USA total field which we do not want to include, as it is already in the self.usa_all
        # it is identified as a null in "state" column.
        self.body = self.body[
            ~((self.body["country"] == "US") & (self.body["state"].isnull()))
        ]

        # addl etl_loadtime field
        self.body["etl_load_time"] = dt.datetime.now()

    def load(self):

        # TODO: make this differently
        self.database.insert_to_table(self.body)

    def teardown(self):

        # TODO: execute swap command
        self.database.swap_tables()

    def run_pipeline(self):

        self.setup()
        self.extract()
        self.transform()
        self.load()
        self.teardown()

