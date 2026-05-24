# Gaia Architecture

This document summarizes the current Gaia architecture and runtime layers.

## Main Layers

-   **Notebook support**: n8n node is used in notebooks for data preparation
-   **Application APIs**: Plant Recognition API, Plant Care RAG API, and Plant Care LLM API
-   **Frontend**: browser client served by nginx
-   **Storage and services**: Apache Hive (historical tables) and optional S3 image storage
-   **Deployment**: local Docker Compose and AWS EC2 (Terraform + Docker Compose)

## AI Components

-   **Image classification (one model)**: Plant Recognition API uses the ViT checkpoint `juppy44/plant-identification-2m-vit-b` (see `docs/apis/plant-recognition.md`). Older notebooks (`ModeloCNN.ipynb`, etc.) are exploratory; they are not separate production models.
-   **LLM with fine-tuning**: Plant Care LLM API loads a user-specific Hugging Face causal model (default repo `plantas-llm-finetuned`; see `docs/apis/plant-care-llm.md`).
-   **LLM with RAG**: Plant Care RAG API retrieves context with FAISS, then calls Groq (`llama-3.3-70b-versatile`) to generate the answer — a standard hosted LLM, not a second classifier (see `docs/apis/plant-care.md`).

## Storage (S3)

We use AWS S3 to store uploaded plant images:

-   Images are uploaded when plant recognition confidence >= 25%
-   Each user gets their own folder in the S3 bucket (named after their username)
-   Bucket name and credentials are configured via `.env`

## Infrastructure References

-   Terraform AWS config: `infra/terraform/`
-   EC2 bootstrap script: `infra/terraform/command.sh`
-   Local stack orchestration: `docker-compose.yml`
-   Build and deploy commands: `Makefile`
-   Hive schema/bootstrap context: `infra/logs/hive_schema.sql`
-   n8n notebook support flow: `projects/n8n/getPlantCareData.json`
-   n8n usage notes: `docs/n8n/flows.md`

## Architecture Diagrams

This page uses the same canonical diagrams defined in:

-   Simple architecture diagram: `README.md`
-   Detailed architecture diagram: `docs/README.md`

The two diagrams above are the project references and should be used as the source of truth.
