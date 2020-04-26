BEGIN TRANSACTION;
DROP TABLE IF EXISTS reporting.covid_daily_new;
ALTER SCHEMA reporting OWNER TO airflow;

CREATE TABLE IF NOT EXISTS reporting.covid_daily
(   
    country         VARCHAR(50)
    state           VARCHAR(50)
    latitude        DECIMAL(9,6)
    longitude       DECIMAL(9,6)
    date            DATETIME
    confirmed       INTEGER
    death           INTEGER
);

ALTER TABLE reporting.covid_daily OWNER TO airflow;
GRANT SELECT ON reporting.covid_daily TO PUBLIC;;

CREATE TABLE IF NOT EXISTS reporting.covid_daily_new
(
    country         VARCHAR(50)
    state           VARCHAR(50)
    latitude        DECIMAL(9,6)
    longitude       DECIMAL(9,6)
    date            DATETIME
    confirmed       INTEGER
    death           INTEGER
);

ALTER TABLE reporting.covid_daily_new OWNER TO airflow;

COMMIT;
