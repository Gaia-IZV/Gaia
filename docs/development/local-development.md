# Local Development

This guide explains how to run Gaia locally for development.

## Requirements

-   Docker and Docker Compose
-   Python 3.12+ (if running services without Docker)
-   Make
-   A valid environment file at `projects/api/.env`

Create the environment file from the template:

```bash
cp projects/api/.env.example projects/api/.env
```

## Option 1: Local Stack with Docker (Recommended)

Run the full stack with frontend + the three APIs:

```bash
make up
```

Services:

-   Frontend: `http://localhost:8080`
-   Plant Recognition API (via frontend proxy): `/api/r/*`
-   Plant Care LLM API (via frontend proxy): `/api/c/*`
-   Plant Care RAG API (via frontend proxy): `/api/c-rag/*`

Useful commands:

```bash
make logs
make down
```

## Option 2: Run Services Without Docker

Run each API in its own terminal:

```bash
cd projects/api/plant_recognition
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

```bash
cd projects/api/plant_care
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

```bash
cd projects/api/plant_care_llm
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Run frontend static files:

```bash
cd projects/frontend
python -m http.server 5500
```

## Related Files

-   Stack orchestration: `docker-compose.yml`
-   Command shortcuts: `Makefile`
-   API env template: `projects/api/.env.example`
-   Frontend API base config: `docker/frontend/api-bases.prod.js`
