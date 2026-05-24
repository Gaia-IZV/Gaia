# Plant Care API

The Plant Care API (RAG path) answers care-related questions using semantic search over a plant dataset, then a hosted LLM (Groq) — not a second image classifier.

## Data Pipeline

1. **Data Preparation**: Data is prepared from notebooks (with optional help from an n8n node)
2. **Storage**: Processed data is versioned and moved into the API data assets
3. **Indexing**: A FAISS index is built from the curated dataset
4. **Semantic Search**: We use **FAISS** (vector search) to perform similarity search over plant embeddings
5. **LLM Response**: Results are sent to **Groq API** (LLM) to generate natural responses in Spanish

## LLM

We use **Groq** as the LLM provider:

-   Model: `llama-3.3-70b-versatile`
-   The LLM transforms the raw search results into friendly, natural Spanish text

## Related Code

-   API entrypoint: `projects/api/plant_care/main.py`
-   Semantic search logic: `projects/api/plant_care/plant_semantic_search.py`
-   FAISS index build script: `projects/api/plant_care/build_faiss_index.py`
-   Python dependencies: `projects/api/plant_care/requirements.txt`
-   Docker runtime image: `docker/plant-care-api/Dockerfile`
-   Shared environment file: `projects/api/.env` and `projects/api/.env.example`

## Related Notebooks

-   `projects/notebooks/llm_semantic_serach.ipynb`
-   `projects/notebooks/LLM.ipynb`

## Endpoint Summary

-   `GET /plant?q=...&k=...`
-   `POST /plant` with JSON body (`query`, `k`)
-   `GET /health`

When running behind frontend nginx:

-   This API is exposed at `/api/c-rag/*`
-   `/api/c/*` is reserved for the Plant Care LLM API

## Quick Local Run

```bash
cd projects/api/plant_care
python main.py
```
