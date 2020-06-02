DROP VIEW IF EXISTS country_daily;
DROP VIEW IF EXISTS country_overall;
DROP VIEW IF EXISTS state_daily;
DROP VIEW IF EXISTS state_overall;
DROP VIEW IF EXISTS log_lat_daily;
DROP VIEW IF EXISTS log_lat_overall;

CREATE VIEW country_daily
    AS
    SELECT  country,
            date,
            SUM(confirmed) AS confirmed,
            SUM(death) AS death
    FROM covid_daily
    GROUP BY country, date ;;

CREATE VIEW country_overall
    AS
    SELECT  country,
            SUM(confirmed) AS confirmed,
            SUM(death) AS death
    FROM covid_daily
    GROUP BY country ;;

CREATE VIEW state_daily
    AS
    SELECT  country,
            state,
            date,
            SUM(confirmed) AS confirmed,
            SUM(death) AS death
    FROM covid_daily
    GROUP BY country, state, date ;;

CREATE VIEW state_overall
    AS
    SELECT  country,
            state,
            SUM(confirmed) AS confirmed,
            SUM(death) AS death
    FROM covid_daily
    GROUP BY country, state ;;

CREATE VIEW log_lat_daily
    AS
    SELECT  longitude,
            latitude,
            date,
            SUM(confirmed) AS confirmed,
            SUM(death) AS death
    FROM covid_daily
    GROUP BY longitude, latitude, date ;;

CREATE VIEW log_lat_overall
    AS
    SELECT  longitude,
            latitude,
            SUM(confirmed) AS confirmed,
            SUM(death) AS death
    FROM covid_daily
    GROUP BY longitude, latitude ;;
