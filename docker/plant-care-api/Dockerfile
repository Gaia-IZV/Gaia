FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=0 \
    PLANT_CARE_CSV=/app/data/cuidados_plantas.csv \
    PLANT_CARE_FAISS_INDEX=/app/data/plants_faiss.index \
    PLANT_CARE_PORT=5001

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY docker/plant-care-api/requirements-runtime.txt /tmp/requirements-runtime.txt
COPY static/data/cuidados_plantas.csv /app/data/cuidados_plantas.csv
COPY projects/plant-care-api/main.py \
    projects/plant-care-api/plant_semantic_search.py \
    projects/plant-care-api/build_faiss_index.py \
    ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /tmp/requirements-runtime.txt && \
    rm /tmp/requirements-runtime.txt

# Precompute FAISS so runtime only loads CSV + index + model (no ~3k encodings per container start).
RUN python build_faiss_index.py

EXPOSE 5001

CMD ["python", "main.py"]
