# Gaia

Web application to assist plant caregivers, utilizing AI.

## Architecture Overview

The system is composed of several components, including data scraping, processing, storage, and a frontend for visualization.

```mermaid
graph TD;

    N8N --> EMR
    EMR --> FLUME
    HUE --> HDFS
    FLUME --> HDFS

    API --> HDFS
    API --> LLM
    API --> CLASSIFICATION_MODEL

    FRONT --> API
    FRONT --> MONGODB
    FRONT --> S3
```

For more details, see the [documentation](docs/architecture.md).

## APIs (`projects/api/`)

Las APIs viven bajo `projects/api/` con dos servicios:

-  **`plant_recognition/`** — visión: identificación de planta en una imagen (puerto 5000).
-  **`plant_care/`** — búsqueda semántica sobre el CSV de cuidados (puerto 5001).

Variables de entorno compartidas: copia `projects/api/.env.example` a `projects/api/.env` (por ejemplo `HF_TOKEN`).

## Plant Recognition API

API para reconocimiento de plantas utilizando modelos de visión por computadora.

### Instalación

```bash
cd projects/api/plant_recognition
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Ejecución

```bash
python main.py
```

La API estará disponible en `http://localhost:5000`

### Endpoints

#### POST /recognize

Reconoce una imagen de planta y devuelve las 5 predicciones más probables.

**Ejemplo de uso:**

```bash
curl -X POST -F "image=@ruta/imagen.jpg" http://localhost:5000/recognize
```

**Respuesta:**

```json
{
   "predictions": [
      { "plant": "Rosa chinensis", "probability": 0.4521 },
      { "plant": "Rosa canina", "probability": 0.2305 },
      { "plant": "Rosa gallica", "probability": 0.1203 },
      { "plant": "Rosa rugosa", "probability": 0.0892 },
      { "plant": "Rosa multiflora", "probability": 0.0456 }
   ]
}
```

#### GET /health

Verifica que la API esté funcionando.

```bash
curl http://localhost:5000/health
```

### Variables de entorno

En `projects/api/`, copia `.env.example` a `.env` y configura:

-  `HF_TOKEN`: Token de Hugging Face para modelos privados (requerido para modelos gated)

### Requisitos

-  Python 3.12+
-  torch
-  transformers
-  flask
-  Pillow
-  numpy<2

## Plant Care API (búsqueda semántica)

### Instalación

```bash
cd projects/api/plant_care
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Ejecución

```bash
python main.py
```

Disponible en `http://localhost:5001`. Endpoints: `GET /health`, `GET /plant?q=...&k=1`, `POST /plant` con JSON `{"query":"...","k":3}`.

Docker y `make` siguen usando las imágenes `docker/plant-recognition-api` y `docker/plant-care-api`.
