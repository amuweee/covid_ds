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
    def __init__(self, worldpopdb=WorldPopUpdates()):

        self.database = worldpopdb
        self.body = pd.DataFrame()

        # Static properties
        self.source_url = WorldPopConfig.POP_URL
        self.header_dict = WorldPopConfig.HEADER_DICT

    def setup(self):

        self.database.drop_existing_table()

    def extract(self):

        response = requests.get(self.source_url)
        data = BeautifulSoup(response.content, features="lxml").find_all("table")

        self.body = pd.read_html(str(data))[0]

    def transform(self):

        self.body.rename(columns=self.header_dict, inplace=True)
        self.body.replace({"N.A.": np.NaN}, inplace=True)

    def load(self):

        self.database.create_insert_table(self.body)

    def teardown(self):
        pass

    def run_pipeline(self):

        self.setup()
        self.extract()
        self.transform()
        self.load()
        self.teardown()
