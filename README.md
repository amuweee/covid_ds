# COVID-19 Data Science


**Disclaimer: This project is for fun and learning purpose, take the predictions with a grain of salt**

This repository contains codes and scripts related to extracting daily infected and death data from gitrepo maintained by [JHUCSSE COVID-19 Data](https://github.com/CSSEGISandData/COVID-19).
The timeseries data is transformed and stored into `covid_master.db` SQLite3 database for use with the datascience workflow.

### Installing

This repo was created with python version 3.6
Run the following to install required packages 

```
pip install -r requirements.txt
```

## Project Structure

Project is separated into multiple sections
- **ETL** Retrieving COVID-19 infected and death data, along with world population data 

### ETL 

All data availa
Run below command to download and store into a local SQLite database
```
python run_etl.py
```
#TODO: Add a shell script to run the file periodically

### Map Visualization



### Prediction