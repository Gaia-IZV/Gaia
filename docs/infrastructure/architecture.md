# Gaia Architecture

This document summarizes the current Gaia architecture and runtime layers.

## Main Layers

-   **Notebook support**: n8n node is used in notebooks for data preparation
-   **Application APIs**: Plant Recognition API, Plant Care RAG API, and Plant Care LLM API
-   **Frontend**: browser client served by nginx
-   **Storage and services**: Apache Hive (historical tables) and optional S3 image storage
-   **Deployment**: local Docker Compose and AWS EC2 (Terraform + Docker Compose)

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
