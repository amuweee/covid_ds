# COVID-19 Data Science


**Disclaimer: This project is for fun and learning purpose, take the predictions with a grain of salt**

This repository contains codes and scripts related to extracting daily infected and death data from gitrepo maintained by [JHUCSSE COVID-19 Data](https://github.com/CSSEGISandData/COVID-19).  
World population data scraped from [Worldometer](https://www.worldometers.info/world-population/population-by-country/).  
The timeseries data is transformed and stored into `covid_master.db` SQLite3 database for use with the datascience workflow.

### Installing

This repo was created with python version 3.6 and a virtual environment is recommended
natigate to the project root and run following commands to setup and install preprequisites

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Project Structure

Project is separated into multiple sections
- **ETL** Retrieving COVID-19 infected and death data, along with world population data 

### ETL 

All data availa
Run below command under virtual environment to download and store into a local SQLite databases
```
python run_etl.py
```
To schedule the etl to run periodically run the following in the project root directory to run at midnight (your computer's time) every day. Note that only the covid database is updated.
```
chmod +x run_etl.py
crontab -e 
```
and add the below line to the bottom of the line
```
00 00 * * * /path/to/project/.venv/bin/python /path/to/project/run_etl.py >> /path/to/log.log 2>&1
```

### Map Visualization



### Prediction