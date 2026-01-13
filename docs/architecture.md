# Gaia Architecture

This document provides a detailed overview of the Gaia system architecture.

## Components

-  **n8n Scraping**: Automates data collection.
-  **Amazon EMR**: Processes large-scale data.
-  **Apache Flume**: Streams data to storage.
-  **MongoDB**: Stores structured data.
-  **S3**: Stores images and other unstructured data.
-  **FastAPI**: Provides an API for accessing data and models.
-  **HuggingFace Model**: AI model for plant care recommendations.
-  **React Frontend**: User interface for visualization.
-  **Hue**: Data visualization tool for processed data.

## Architecture Diagram

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
