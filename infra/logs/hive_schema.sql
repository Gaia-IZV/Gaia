-- Database creation
CREATE DATABASE IF NOT EXISTS gaia;

-- Table for plant recognition events (confidence >= 25%)
CREATE TABLE IF NOT EXISTS gaia.plant_recognition_events (
    id STRING,
    username STRING,
    plant_name STRING,
    confidence DOUBLE,
    s3_url STRING,
    event_timestamp STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;

-- User plant-care queries (what was asked, from which API)
CREATE TABLE IF NOT EXISTS gaia.plant_care_queries (
    id STRING,
    username STRING,
    query STRING,
    source STRING,
    k INT,
    event_timestamp STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;

-- Model responses linked to a query row
CREATE TABLE IF NOT EXISTS gaia.plant_care_responses (
    id STRING,
    query_id STRING,
    model_id STRING,
    response STRING,
    fallback_reason STRING,
    event_timestamp STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;
