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


