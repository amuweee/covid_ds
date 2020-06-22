import etl.covid_daily
import etl.worldpop
import os.path
from utils import project_root
from etl.constants import WorldPopConfig

if __name__ == "__main__":

    # Check if database exsit and whether to download population db
    # root_path = project_root()
    # db = WorldPopConfig.DB_NAME
    # if os.path.isfile(f"{root_path}/{db}.db") == False:
    run_worldpop = etl.worldpop.WorldPopPipepine()
    run_worldpop.run_pipeline()

    # Run covid daily update
    run_etl = etl.covid_daily.CovidPipeline()
    run_etl.run_pipeline()
