# Plant Care API

The Plant Care API answers care-related questions using semantic search over a plant dataset.

## Related Code

-  API entrypoint: `projects/api/plant_care/main.py`
-  Semantic search logic: `projects/api/plant_care/plant_semantic_search.py`
-  FAISS index build script: `projects/api/plant_care/build_faiss_index.py`
-  Python dependencies: `projects/api/plant_care/requirements.txt`
-  Docker runtime image: `docker/plant-care-api/Dockerfile`
-  Shared environment file: `projects/api/.env` and `projects/api/.env.example`

## Related Notebooks

-  `projects/notebooks/llm_semantic_serach.ipynb`
-  `projects/notebooks/LLM.ipynb`

## Endpoint Summary

-  `GET /plant?q=...&k=...`
-  `POST /plant` with JSON body (`query`, `k`)
-  `GET /health`

## Quick Local Run

```bash
cd projects/api/plant_care
python main.py
```
