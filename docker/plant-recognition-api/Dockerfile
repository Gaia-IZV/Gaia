FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=0

RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY docker/plant-recognition-api/requirements-runtime.txt /tmp/requirements-runtime.txt
COPY projects/api/main.py projects/api/image_recognition_model.py ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /tmp/requirements-runtime.txt && \
    rm /tmp/requirements-runtime.txt

EXPOSE 5000

CMD ["python", "main.py"]
