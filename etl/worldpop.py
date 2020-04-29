# webscraping code from
# https://www.kaggle.com/tanuprabhu/population-by-country-2020

import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

from etl.constants import WorldPopConfig
from utils import WorldPopUpdates


class WorldPopPipepine:
    """ Class for handling tasks associated with retrieving, transforming to database setup, and writing to SQLite db

    Payload and interface
    ---------------------
    All intermediate data storage and transformation are performed in pd.DataFrames
    Once complete, open/create the databse connection and update/store the data

    Pipeline
    --------
    1. Setup
        i) Drop existing tables if exist
    2. Extract
        i) Scrape table data from source with BeautifulSoup
    3. Transform
        i) Transform and clearn column headers
    4. Load
        i) Insert DataFrame into the database
    5. Teardown
        i) None
    """
    def __init__(self, worldpopdb=WorldPopUpdates()):
        # Payload and sql interface
        self.database = worldpopdb
        self.body = pd.DataFrame()

        # Static properties
        self.source_url = WorldPopConfig.POP_URL
        self.header_dict = WorldPopConfig.HEADER_DICT

    def setup(self):
        """Drop existin table if exists
        """

        self.database.drop_existing_table()

    def extract(self):
        """Scrape the web data using BeautifulSoup, read content into a pd.DataFrame
        """

        response = requests.get(self.source_url)
        data = BeautifulSoup(response.content, features="lxml").find_all("table")

        self.body = pd.read_html(str(data))[0]

    def transform(self):
        """Rename the columns appropriately to remove blank spaces and special characters
        Also replaces 'N.A.' stored as string with np.NaN
        """

        self.body.rename(columns=self.header_dict, inplace=True)
        self.body.replace({"N.A.": np.NaN}, inplace=True)

    def load(self):
        """Insert DataFrame into database
        """

        self.database.create_insert_table(self.body)

    def teardown(self):
        pass

    def run_pipeline(self):
        """Defines pipeline steps
        """

        self.setup()
        self.extract()
        self.transform()
        self.load()
        self.teardown()
