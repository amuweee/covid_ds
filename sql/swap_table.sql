BEGIN TRANSACTION;
    ALTER TABLE reporting.covid_daily RENAME TO covid_daily_old;
    ALTER TABLE reporting.covid_daily_new RENAME TO covid_daily;
    GRANT SELECT ON reporting.covid_daily TO PUBLIC;
    DROP TABLE reporting.covid_daily_old;
COMMIT; 