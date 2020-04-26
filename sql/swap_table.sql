BEGIN TRANSACTION;
ALTER TABLE covid_daily RENAME TO covid_daily_old;
ALTER TABLE covid_daily_new RENAME TO covid_daily;
DROP TABLE IF EXISTS covid_daily_old;
END TRANSACTION;