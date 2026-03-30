# n8n Flow (Data Ingestion)

Gaia uses n8n to collect and export plant care data used by backend search components.

## Related Files

-  Flow JSON: `projects/n8n/getPlantCareData.json`
-  Detailed flow notes: `docs/n8n/flows.md`
-  Plant Care semantic search: `projects/api/plant_care/plant_semantic_search.py`
-  Index builder: `projects/api/plant_care/build_faiss_index.py`

## Output

The flow fetches external API data and exports structured records (Google Sheets/CSV), later consumed by the Plant Care API pipeline.
