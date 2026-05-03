# Documentation Index

## Architecture Diagram (Detailed)

```mermaid
graph TD;

    %% ───────────────
    %% Notebooks / Preparation
    %% ───────────────
    subgraph PREP["Notebook Support Layer"]
        N8N["n8n node (notebook usage)"] --> NOTEBOOKS["Notebooks / data preparation"]
    end


    %% ───────────────
    %% Runtime Data Platform
    %% ───────────────
    subgraph BIGDATA["Runtime Data Platform"]
        HIVE["Apache Hive"]
        S3
    end


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
        API["Recognition API + Care RAG API + Care LLM API"]
    end

    NOTEBOOKS --> API
    API --> HIVE
    API --> LLM
    API --> PRETRAINED_MODEL
    API --> KERAS_MODEL
    API --> S3


    %% ───────────────
    %% Frontend
    %% ───────────────
    subgraph FRONTEND["Presentation Layer"]
        FRONT
    end

    FRONT --> API

```

## Development

-   Local development: `docs/development/local-development.md`

## APIs

-   Plant Recognition API: `docs/apis/plant-recognition.md`
-   Plant Care API: `docs/apis/plant-care.md`
-   Plant Care LLM API: `docs/apis/plant-care-llm.md`

## Frontend

-   Frontend overview: `docs/frontend/overview.md`

## Infrastructure

-   Architecture: `docs/infrastructure/architecture.md`
-   AWS deployment with Terraform: `docs/infrastructure/deployment-aws.md`
-   n8n ingestion flow context: `docs/infrastructure/n8n-flow.md`
-   n8n flow documentation: `docs/n8n/flows.md`
