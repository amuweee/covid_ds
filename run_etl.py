#! python

import etl.covid_daily

if __name__ == "__main__":
    run_etl = etl.covid_daily.CovidPipeline()
    run_etl.run_pipeline()