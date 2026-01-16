# Gaia Architecture

This document provides a detailed overview of the Gaia system architecture.

## Components

-  **n8n Scraping**: Automates data collection.
-  **Amazon EMR**: Processes large-scale data.
-  **Apache Flume**: Streams data to storage.
-  **HDFS**: Stores large-scale processed and raw data.
-  **Hue**: Data visualization tool for processed data.
-  **FastAPI**: Provides an API for accessing data and models.
-  **Fine-tuned LLM**: Provides natural language processing capabilities via the backend API.
-  **Classification Model**: Performs image classification and exposes inference through the backend API.
-  **React Frontend**: Provides the user interface for interacting with the system.
-  **MongoDB**: Stores structured application data.
-  **S3**: Stores unstructured data such as images and assets.

## Architecture Diagram

```mermaid
graph TD;

    %% ───────────────
    %% Data Ingestion
    %% ───────────────
    subgraph INGESTION["Data Ingestion and Orchestration"]
        N8N --> EMR --> FLUME
    end


    %% ───────────────
    %% Big Data Platform
    %% ───────────────
    subgraph BIGDATA["Big Data Platform"]
        HDFS
        HUE
    end

    FLUME --> HDFS
    HUE --> HDFS


    %% ───────────────
    %% AI Models
    %% ───────────────
    subgraph AI["Artificial Intelligence Layer"]

        LLM

        subgraph CLASSIFICATION["Image Classification System"]
            PRETRAINED_MODEL["Pretrained Classification Model"]
            KERAS_MODEL["Custom Classification Model (Keras)"]
        end
    end


    %% ───────────────
    %% Backend
    %% ───────────────
    subgraph BACKEND["Application Backend"]
        API
    end

    API --> HDFS
    API --> LLM
    API --> PRETRAINED_MODEL
    API --> KERAS_MODEL


    %% ───────────────
    %% Application Storage
    %% ───────────────
    subgraph STORAGE["Application Persistence Layer"]
        STORAGE_FACADE["Persistence Service"]
        MONGODB
        S3

        STORAGE_FACADE --> MONGODB
        STORAGE_FACADE --> S3
    end


    %% ───────────────
    %% Frontend
    %% ───────────────
    subgraph FRONTEND["Presentation Layer"]
        FRONT
    end

    FRONT --> API
    FRONT --> STORAGE_FACADE

```
