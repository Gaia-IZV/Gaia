# Plant Care API

The Plant Care API answers care-related questions using semantic search over a plant dataset.

## Data Pipeline

1. **Data Collection**: Data is collected using **n8n** workflows
2. **Storage**: The collected data is stored in **Google Drive**
3. **Training**: Data is downloaded from Drive to train our model
4. **Semantic Search**: We use **FAISS** (vector search) to perform similarity search over plant embeddings
5. **LLM Response**: Results are sent to **Groq API** (LLM) to generate natural responses in Spanish

## LLM

We use **Groq** as the LLM provider:
- Model: `llama-3.3-70b-versatile`
- The LLM transforms the raw search results into friendly, natural Spanish text

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
