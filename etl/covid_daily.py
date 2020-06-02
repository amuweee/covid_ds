# Source data at
# https://github.com/CSSEGISandData/COVID-19

import datetime as dt
import numpy as np
import pandas as pd
import requests
import csv
from io import StringIO

pd.options.mode.chained_assignment = None

from etl.constants import ETLConfigs
from utils import DBUpdates, CreateViews


class CovidPipeline:
    """ Class for handling tasks associated with retrieving, transforming to database setup, and writing to SQLite db

    Payload and interface
    ---------------------
    All intermediate data storage and transformation are performed in pd.DataFrames
    Once complete, open/create the databse connection and update/store the data

    Pipeline
    --------
    1. Setup
        i) Create staging table
    2. Extract
        i) Extract csv file from source gitrepo
    3. Transform
        i) Transform and merge the data
    4. Load
        i) Insert dataframes into staging table
    5. Teardown
        i) Swap staging and drop old table
    """

    def __init__(self, dbupdates=DBUpdates(), createviews=CreateViews()):
        # Payload and sql interface
        self.database = dbupdates
        self.createviews = createviews
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
        This will create a new staging table
        """
        self.database.create_table()

    def extract(self):
        """Executes the source script for daily covid timeseries data where the csv files hosted
        on the source gitrepo and store to individual dataframes
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
        """Transform each dataframe to calculate the daily deltas, as well as reformatting the date
        Then merge all dataframes together, and unpivot the dates so that it'll be in a database friendly format
        """

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
        """Load the finalized DataFrame into the staging table in databse
        """

        self.database.insert_to_table(self.body)

    def teardown(self):
        """Swap the existing to old, stage to new, and drop the old
            Creates views after the swap
        """

        self.database.swap_tables()
        self.createviews.create_views()

    def run_pipeline(self):
        """Defines pipeline steps
        """

        self.setup()
        self.extract()
        self.transform()
        self.load()
        self.teardown()
