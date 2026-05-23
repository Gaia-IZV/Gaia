# Plant Care LLM API

The Plant Care LLM API serves plant care answers using a Hugging Face model associated with the authenticated user.

## Model Strategy

-   Primary model: `{whoami_username}/{HF_REPO_NAME}` (default repo name: `plantas-llm-finetuned`)
-   Optional fallback model: `HF_FALLBACK_MODEL_ID` (empty by default; only used if you set it explicitly)
-   Authentication: `HF_TOKEN` is required

## Loading Notes

The service loads the model similarly to the working notebook flow:

-   `device_map="auto"` by default (toggle with `HF_USE_DEVICE_MAP`)
-   `torch_dtype=torch.bfloat16`

If you need `device_map="auto"`, the Docker image includes `accelerate`.

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

When `USING_EMR=true` and `EMR_IP` is set, this API logs to:

-   `gaia.plant_care_queries` (`source=llm`, user question in `query`)
-   `gaia.plant_care_responses` (full model output, `model_id`, optional `fallback_reason`)

Same tables as the RAG-based Plant Care API (`source=rag`).

## Quick Local Run

```bash
cd projects/api/plant_care_llm
python main.py
```
