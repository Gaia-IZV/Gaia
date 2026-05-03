# Plant Care LLM API

The Plant Care LLM API serves plant care answers using a Hugging Face model associated with the authenticated user.

## Model Strategy

-   Primary model: `{whoami_username}/{HF_REPO_NAME}` (default repo name: `plantas-llm-finetuned`)
-   Fallback model: `HF_FALLBACK_MODEL_ID` (default: `Qwen/Qwen2.5-0.5B-Instruct`)
-   Authentication: `HF_TOKEN` is required

## Related Code

-   API entrypoint: `projects/api/plant_care_llm/main.py`
-   Python dependencies: `projects/api/plant_care_llm/requirements.txt`
-   Docker runtime image: `docker/plant-care-llm-api/Dockerfile`
-   Docker runtime requirements: `docker/plant-care-llm-api/requirements-runtime.txt`
-   Shared environment file: `projects/api/.env` and `projects/api/.env.example`

## Endpoint Summary

-   `GET /health`
-   `GET /whoami`
-   `POST /generate` with JSON body (`prompt` or `planta`, optional `max_new_tokens`, `temperature`, `username`)
-   `GET /generate?prompt=...` (or `planta=...`)

## Hive Logging

When `USING_EMR=true` and `EMR_IP` is set, this API logs care requests to:

-   `gaia.plant_care_queries`

This keeps the same historical table used by the RAG-based care API.

## Quick Local Run

```bash
cd projects/api/plant_care_llm
python main.py
```
