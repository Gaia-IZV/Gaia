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

-- Table for plant care queries (optional, for tracking user queries)
CREATE TABLE IF NOT EXISTS gaia.plant_care_queries (
    id STRING,
    username STRING,
    query STRING,
    response_preview STRING,
    event_timestamp STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;
