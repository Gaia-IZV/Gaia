# Frontend Overview

The frontend is a lightweight web client that sends image uploads to Plant Recognition and text/image-derived plant names to either Plant Care RAG or Plant Care LLM.

## Pages

-   **login.html**: Welcome page where users enter their name
-   **login.js**: Handles login logic, stores username in localStorage, redirects to main page
-   **index.html**: Main chat interface
-   **script.js**: Main client logic

## Related Code

-   UI markup: `projects/frontend/index.html`
-   Login page: `projects/frontend/login.html`
-   Login logic: `projects/frontend/login.js`
-   Styles: `projects/frontend/styles.css`
-   Main client logic: `projects/frontend/script.js`
-   Base URL config: `projects/frontend/api-bases.js`
-   Production API bases: `docker/frontend/api-bases.prod.js`
-   Frontend image build: `docker/frontend/Dockerfile`
-   Reverse proxy config: `docker/frontend/nginx.conf`

## Authentication

Users must enter their name on the login page. The username is stored in `localStorage` under the key `gaia_username`. Without a valid session, users are redirected back to login.html.

The username is used to create a dedicated folder in our S3 bucket where images are stored when uploaded for plant recognition (only when confidence >= 25%).

## How It Connects

-   `/api/c/*` is proxied to Plant Care LLM (`5002`)
-   `/api/c-rag/*` is proxied to Plant Care RAG (`5001`)
-   `/api/r/*` is proxied to Plant Recognition (`5000`)
-   In local non-docker mode, `api-bases.js` points to localhost API ports

## Model Selection

The main chat UI includes a model selector so users can choose:

-   **LLM Fine-tuned (Hugging Face)**: uses `/api/c/*`
-   **RAG + Groq**: uses `/api/c-rag/*`

The selected option is persisted in `localStorage` with key `gaia_care_provider`.

## Quick Local Run

```bash
cd projects/frontend
python -m http.server 5500
```
