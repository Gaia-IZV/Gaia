-- Base de datos analítica del proyecto Gaia
CREATE DATABASE IF NOT EXISTS gaia;

-- Eventos de reconocimiento de planta por imagen (solo si confidence >= 25%)
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

-- Consultas de cuidado de plantas (pregunta del usuario, sin respuesta del modelo)
CREATE TABLE IF NOT EXISTS gaia.plant_care_queries (
    id STRING,              
    username STRING,       
    query STRING,           -- Texto de la pregunta (RAG) o planta/prompt resumido (LLM)
    source STRING,          -- API de origen: 'rag' (plant_care) o 'llm' (plant_care_llm)
    k INT,                  -- Top-k de búsqueda semántica; NULL si source = 'llm'
    event_timestamp STRING 
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;

-- Respuestas del modelo asociadas a una consulta en plant_care_queries
CREATE TABLE IF NOT EXISTS gaia.plant_care_responses (
    id STRING,
    query_id STRING,
    model_id STRING,
    response STRING,
    fallback_reason STRING, -- Motivo del modelo de respaldo; NULL si no hubo fallback
    event_timestamp STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|'
STORED AS TEXTFILE;
