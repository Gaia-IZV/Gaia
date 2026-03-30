# Frontend Overview

The frontend is a lightweight web client that sends text queries to Plant Care and image uploads to Plant Recognition.

## Related Code

-  UI markup: `projects/frontend/index.html`
-  Styles: `projects/frontend/styles.css`
-  Main client logic: `projects/frontend/script.js`
-  Base URL config: `projects/frontend/api-bases.js`
-  Production API bases: `docker/frontend/api-bases.prod.js`
-  Frontend image build: `docker/frontend/Dockerfile`
-  Reverse proxy config: `docker/frontend/nginx.conf`

## How It Connects

-  `/api/c/*` is proxied to Plant Care (`5001`)
-  `/api/r/*` is proxied to Plant Recognition (`5000`)
-  In local non-docker mode, `api-bases.js` points to localhost API ports

## Quick Local Run

```bash
cd projects/frontend
python -m http.server 5500
```
