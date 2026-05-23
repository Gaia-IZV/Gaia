FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=0 \
    PLANT_CARE_LLM_PORT=5002

COPY docker/plant-care-llm-api/requirements-runtime.txt /tmp/requirements-runtime.txt
COPY projects/api/hive_plant_care_log.py \
    projects/api/plant_care_llm/main.py \
    ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /tmp/requirements-runtime.txt && \
    rm /tmp/requirements-runtime.txt

EXPOSE 5002

CMD ["python", "main.py"]
