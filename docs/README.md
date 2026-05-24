# Documentation Index

Runtime AI stack: **one** image classifier (ViT), **two** LLM paths (fine-tuned Hugging Face model vs. FAISS retrieval + Groq).

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

        subgraph CLASSIFICATION["Image Classification"]
            VIT_MODEL["ViT classifier (Hugging Face)"]
        end

        subgraph LLMS["Language Models"]
            LLM_FT["Fine-tuned LLM (Hugging Face)"]
            subgraph RAG_PIPELINE["RAG pipeline"]
                FAISS["FAISS semantic search"]
                GROQ_LLM["Groq LLM (llama-3.3-70b)"]
                FAISS --> GROQ_LLM
            end
        end
    end


    %% ───────────────
    %% Backend
    %% ───────────────
    subgraph BACKEND["Application Backend"]
        REC_API["Plant Recognition API"]
        CARE_RAG_API["Plant Care RAG API"]
        CARE_LLM_API["Plant Care LLM API"]
    end

    NOTEBOOKS --> REC_API
    NOTEBOOKS --> CARE_RAG_API
    NOTEBOOKS --> CARE_LLM_API
    REC_API --> HIVE
    CARE_RAG_API --> HIVE
    CARE_LLM_API --> HIVE
    REC_API --> VIT_MODEL
    REC_API --> S3
    CARE_RAG_API --> RAG_PIPELINE
    CARE_LLM_API --> LLM_FT


    %% ───────────────
    %% Frontend
    %% ───────────────
    subgraph FRONTEND["Presentation Layer"]
        FRONT
    end

    FRONT --> REC_API
    FRONT --> CARE_RAG_API
    FRONT --> CARE_LLM_API

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
