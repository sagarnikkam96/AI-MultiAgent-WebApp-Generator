# AI-MultiAgent-WebApp-Generator (Version 2)

An autonomous multi-agent full-stack web application generator. Describe any web application using text, voice, images, audio, or video files — 9 autonomous AI agents design, plan, generate, test, debug, security-audit, and containerize full-stack React + FastAPI + SQLAlchemy web applications.

---

## 🤖 9-Agent Autonomous Pipeline

```
USER PROMPT / MULTIMODAL INPUT
  │
  ▼
1. REQUIREMENT AGENT      ── Extracts domain purpose, roles, features, pages & constraints
  │
  ▼
2. DESIGN / PLANNING AGENT ── Formulates 3-tier architecture, layouts, navigation & workflows
  │
  ▼
3. BACKEND AGENT          ── Designs FastAPI REST endpoints, Pydantic schemas & auth
  │
  ▼
4. DATABASE AGENT         ── Designs SQLAlchemy relational tables, relationships & indexes
  │
  ▼
5. CODE AGENT             ── Assembles full-stack React 18, FastAPI, and database code on disk
  │
  ▼
6. TESTING AGENT          ── Validates Python AST syntax, route resolution, models & configs
  │
  ▼
7. DEBUG AGENT (Loop)     ── Diagnoses errors & applies code self-healing repairs
  │
  ▼
8. SECURITY AGENT         ── Audits SQL injection safety, secret exposure, CORS & validation
  │
  ▼
9. DEPLOYMENT AGENT       ── Generates Dockerfiles, docker-compose.yml, .env, and guides
  │
  ▼
GENERATED APPLICATION    ── Build, Live In-Browser Preview & ZIP Download
```

---

## 🚀 Key Features

- **Approval-Gated AI SDLC**: Plan a requirements specification (SRS), review system architecture, database schemas, and API plans, then explicitly approve the design before application generation.
- **Full-Stack Autonomous Generation**: Generates real, executable code files for React 18 (TypeScript + Vite) and FastAPI (Python + SQLAlchemy).
- **Multimodal Inputs**: Supports natural-language text, browser microphone voice input, and file uploads (Images, PDFs, DOCX, TXT, JSON, CSV, Audio, Video).
- **Multilingual Output**: Choose from 20 output languages—English, Hindi, Kannada, Marathi, Telugu, Bengali, Tamil, Gujarati, Malayalam, Punjabi, Odia, Assamese, Urdu, Sanskrit, Nepali, Konkani, Sindhi, Kashmiri, Manipuri (Meitei), and Maithili. The selection is carried through text, voice, multimodal, SDLC planning, and project-generation requests; generation prompts direct user-facing copy to the chosen language. The primary generation screen has localized labels and Urdu, Sindhi, and Kashmiri use right-to-left direction. Full translation coverage for every existing workspace screen and every generated-app template is not yet complete; generated apps currently bundle their original five-language UI dictionaries.
- **Domain Intelligence**: Generates tailored architectures for Healthcare, E-Commerce, Food Delivery, Campus/Education, Finance, Real Estate, Inventory, Hospitality, Railway/Transit, Travel, Fitness, Task Management, and Custom domains.
- **Domain-Matched Visual Design**: Generates a custom SVG brand mark and pairs each generated site with relevant hero photography, such as medical care, campus life, hotel dining, or railway travel.
- **Automated Testing & Self-Healing**: Real Python AST syntax parsing, import resolution, and iterative debug repair loop.
- **AI Maintenance Requests**: Submit a follow-up change request to regenerate the project and run the verification, self-healing, security, and deployment preparation pipeline again.
- **Premium AI Visual Experience**: Prompt-aware art direction selects a visual personality for new websites and offers CSS-only, before/after upgrades for existing built projects. Approve or reject each proposed style; accepted styles are rebuilt and validated with rollback on failure.
- **Security Auditing**: Static security scans detecting SQL injection risks, exposed credentials, CORS vulnerabilities, and input validation schemas.
- **Production Containerization**: Prepares multi-stage `Dockerfile`, `docker-compose.yml`, and production `.env.example`.
- **Live Preview & ZIP Download**: One-click in-browser preview and exportable VS Code-ready project ZIP archive.
- **Personal Website History**: Signed-in users can review their generated websites and build/open previous previews from the workspace history.
- **AI Media Generation**: Procedural AI video storyboard studio and text-to-image generator.

---

## 🛠 Quick Start

### 1. Start Backend FastAPI Server (Port 8000)

```bash
cd backend
# Activate virtual environment
..\.venv\Scripts\activate

# Start backend server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify backend health: `http://127.0.0.1:8000/health`

### 2. Start Frontend Vite UI (Port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 3. One-Click Launcher

```bash
python run_app.py
```

---

## 🔌 REST API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Backend service health and status |
| `POST` | `/analyze` | Execute complete 9-agent generation pipeline |
| `POST` | `/api/sdlc/plan` | Generate a reviewable SRS, architecture, database schema, and API plan without generating code |
| `POST` | `/api/sdlc/generate` | Generate from the submitted requirements/design after explicit approval |
| `POST` | `/api/multimodal/analyze` | Multimodal requirement analysis with uploaded files |
| `POST` | `/projects/{slug}/premium-design/preview` | Stage a prompt-aware CSS visual proposal without changing project files |
| `GET` | `/projects/{slug}/premium-preview/{preview_id}` | View the staged website design comparison |
| `POST` | `/projects/{slug}/premium-design/{preview_id}/accept` | Apply the visual proposal only if the frontend build and project checks pass |
| `DELETE` | `/projects/{slug}/premium-design/{preview_id}` | Reject and discard a staged visual proposal |
| `GET` | `/api/projects/history` | List websites generated by the authenticated user |
| `POST` | `/api/generate-image` | Generate AI image from prompt |
| `POST` | `/api/generate-video` | Generate motion video storyboards and script |
| `POST` | `/api/explain-project` | Generate audio narration script and summary |
| `GET` | `/projects/{slug}` | Status of a generated project |
| `GET` | `/projects/{slug}/test` | Execute on-demand automated test checks |
| `POST` | `/projects/{slug}/debug` | Execute on-demand self-healing debug loop |
| `GET` | `/projects/{slug}/security` | Execute automated security audit |
| `GET` | `/projects/{slug}/deployment` | Retrieve Dockerfile and deployment configurations |
| `POST` | `/projects/{slug}/build` | Install dependencies and compile frontend (`npm run build`) |
| `GET` | `/projects/{slug}/preview[/{path}]` | Serve the live interactive SPA preview |
| `GET` | `/projects/{slug}/download` | Download full project codebase as a ZIP archive |

### Premium Visual Upgrade

Build a generated project, open its **Full-Stack Code & Build** panel, select **Upgrade to Premium Design**, and compare the current and proposed site before accepting or rejecting it. Art direction supports futuristic, luxury, cinematic, creative, editorial, organic, minimalist, glassmorphism, and bold personalities. Automatic direction uses the local Ollama model when it returns a supported result; otherwise the UI identifies the prompt-aware rule-based fallback.

Visual upgrades are additive CSS. They do not replace React components, forms, API calls, database logic, authentication, or routes. The generated styles use existing assets, system font stacks, responsive breakpoints, keyboard focus states, reduced-motion support, and no added frontend dependencies. Accepting a proposal rebuilds the frontend and runs project validation; failure restores the previous stylesheet and built site.

---

## 🧪 Testing Suite

Run all automated unit and integration tests:

```bash
python -m unittest discover -s tests
```
