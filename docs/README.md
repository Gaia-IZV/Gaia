# Documentation Index

## Architecture Diagram (Detailed)

```mermaid
graph TD;

    %% ───────────────
    %% Data Ingestion
    %% ───────────────
    subgraph INGESTION["Data Ingestion and Orchestration"]
        N8N --> EMR --> FLUME
    end


    %% ───────────────
    %% Big Data Platform
    %% ───────────────
    subgraph BIGDATA["Big Data Platform"]
        HDFS
        HUE
    end

    FLUME --> HDFS
    HUE --> HDFS


    %% ───────────────
    %% AI Models
    %% ───────────────
    subgraph AI["Artificial Intelligence Layer"]

        LLM

        subgraph CLASSIFICATION["Image Classification System"]
            PRETRAINED_MODEL["Pretrained Classification Model"]
            KERAS_MODEL["Custom Classification Model (Keras)"]
        end
    end


    %% ───────────────
    %% Backend
    %% ───────────────
    subgraph BACKEND["Application Backend"]
        API
    end

    API --> HDFS
    API --> LLM
    API --> PRETRAINED_MODEL
    API --> KERAS_MODEL


    %% ───────────────
    %% Application Storage
    %% ───────────────
    subgraph STORAGE["Application Persistence Layer"]
        STORAGE_FACADE["Persistence Service"]
        MONGODB
        S3

        STORAGE_FACADE --> MONGODB
        STORAGE_FACADE --> S3
    end


    %% ───────────────
    %% Frontend
    %% ───────────────
    subgraph FRONTEND["Presentation Layer"]
        FRONT
    end

    FRONT --> API
    FRONT --> STORAGE_FACADE

```

## Development

-  Local development: `docs/development/local-development.md`

## APIs

-  Plant Recognition API: `docs/apis/plant-recognition.md`
-  Plant Care API: `docs/apis/plant-care.md`

## Frontend

-  Frontend overview: `docs/frontend/overview.md`

## Infrastructure

-  Architecture: `docs/infrastructure/architecture.md`
-  AWS deployment with Terraform: `docs/infrastructure/deployment-aws.md`
-  n8n ingestion flow context: `docs/infrastructure/n8n-flow.md`
-  n8n flow documentation: `docs/n8n/flows.md`
