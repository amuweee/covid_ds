CREATE TABLE IF NOT EXISTS covid_daily
(   
    country         TEXT,
    state           TEXT,
    latitude        REAL,
    longitude       REAL,
    date            TEXT,
    confirmed       INTEGER,
    death           INTEGER,
    etl_load_time   TEXT
);