#! python

import etl.covid_daily
import etl.worldpop
import sqlite3


if __name__ == "__main__":
    
    run_worldpop = etl.worldpop.WorldPopPipepine()
    run_worldpop.run_pipeline()

    run_etl = etl.covid_daily.CovidPipeline()
    run_etl.run_pipeline()
