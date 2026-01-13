# Gaia

Web application to assist plant caregivers, utilizing AI.

## Architecture Overview

The system is composed of several components, including data scraping, processing, storage, and a frontend for visualization.

```mermaid
graph TD;

    N8N[n8n Scraping]
    EMR[Amazon EMR]
    FLUME[Apache Flume]
    MONGO[MongoDB]
    API[FastAPI]
    MODEL[Modelo IA HuggingFace]
    FRONT[React Frontend]
    HUE[Hue Visualizacion]
    S3[S3 Images]

    N8N --> EMR
    EMR --> FLUME
    FLUME --> MONGO
    FLUME --> S3

    API --> MONGO
    API --> S3
    API --> MODEL
    FRONT --> API
    EMR --> HUE
    FRONT --> EMR
```

For more details, see the [documentation](docs/architecture.md).
