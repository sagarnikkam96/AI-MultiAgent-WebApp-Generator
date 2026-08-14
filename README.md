# AI-MultiAgent-WebApp-Generator

Multi-agent web application generator: describe an app in plain English and it generates a
full React + TypeScript frontend, FastAPI backend, and database schema, then lets you build,
preview, and download the working website.

## How to run

The frontend talks to the backend through the Vite dev proxy, so the backend **must** run on
port **8000**.

### 1. Backend (port 8000)

```bash
cd backend
.venv\Scripts\activate        # or: python -m venv .venv && pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Verify: http://127.0.0.1:8000/health should return `"status": "success"`.

### 2. Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### 3. Generate a website

1. Enter a prompt, e.g. `Build a hospital management system with appointment booking using React FastAPI`.
2. Click **Generate** — this runs the multi-agent pipeline and writes the project to
   `backend/generated_projects/<slug>/`.
3. Click **Build & Preview** — installs dependencies and builds the React frontend.
4. Click **Open Preview** to see the live site, or **Download ZIP** to get the project files.

> The frontend routes `/analyze`, `/health`, and `/projects` to the backend via the Vite proxy
> (see `frontend/vite.config.ts`). The proxy target defaults to `http://127.0.0.1:8000` but is
> configurable. If your backend runs on a different port (e.g. 8001), start the frontend with:
>
> ```bash
> $env:VITE_PROXY_TARGET='http://127.0.0.1:8001'; npm run dev   # PowerShell
> VITE_PROXY_TARGET=http://127.0.0.1:8001 npm run dev            # bash / macOS / Linux
> ```
>
> Keeping the backend on 8000 is simplest (`cd backend; python -m uvicorn app.main:app --reload`).

## Backend API

| Method | Path                                  | Description                                   |
| ------ | ------------------------------------- | --------------------------------------------- |
| GET    | `/health`                             | Backend health/status                         |
| POST   | `/analyze`                            | Run the generation pipeline (returns project) |
| GET    | `/projects/{slug}`                    | Status of a generated project                 |
| GET    | `/projects/{slug}/download`           | Download the project as a ZIP                 |
| POST   | `/projects/{slug}/build`              | npm install + build the generated frontend    |
| GET    | `/projects/{slug}/preview[/{path}]`   | Serve the built website (SPA)                 |

