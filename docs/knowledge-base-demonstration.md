# Knowledge Base — Demonstration Example

A safe demonstration showing how the **Curated Software Development Knowledge Base** provides
technical context to the agent pipeline. This is for illustrating the mechanism to an
evaluator.

> ⚠️ **This is a synthetic example — not real data.** It contains no real patient
> information, names, medical records, phone numbers, or addresses. It is illustrative only;
> we make no claim that these are real patient records.

## USER REQUIREMENT

> "Build a hospital management system using React, FastAPI and PostgreSQL."

## Step 1 — Requirement Analysis

The requirement agent extracts:

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Project name   | hospital management system              |
| Project type   | Healthcare                              |
| Frontend       | React                                   |
| Backend        | FastAPI                                 |
| Database       | PostgreSQL                              |
| Authentication | JWT (login)                             |
| Modules        | Login, Dashboard, Patients, Doctors     |

## Step 2 — Knowledge Retrieval / Technical Context *(planned RAG stage)*

The knowledge base supplies relevant technical context per detected technology:

- **React** → `react/components.md`, `react/state_management.md`
- **FastAPI** → `fastapi/api_design.md`, `fastapi/routing.md`
- **PostgreSQL** → `postgresql/database_design.md`
- **SQLAlchemy** → `sqlalchemy/models.md`, `sqlalchemy/sessions.md`
- **JWT** → `authentication/jwt.md`, `authentication/authorization.md`
- **REST API** → `rest_api/principles.md`, `rest_api/endpoints.md`

*(This stage is documented as planned/future — see `knowledge_base/RAG_INTEGRATION.md`.)*

## Step 3 — Planning Agent

Derives tasks aligned with the documented architecture:

- **Frontend tasks:** create React project, configure routing, build components, API integration
- **Backend tasks:** create API, authentication, business logic
- **Database tasks:** design tables, relationships, seed data

## Step 4 — Backend Agent

Generates a FastAPI backend following `fastapi/*`, `rest_api/*`, and `authentication/*`:

```
POST /auth/login          # JWT login
GET  /patients            # list patients
POST /patients            # create patient
GET  /doctors             # list doctors
POST /appointments        # create appointment
```

Each route uses Pydantic schemas, a `get_db` session dependency, and JWT protection on
sensitive endpoints.

## Step 5 — Database Agent

Generates PostgreSQL/SQLAlchemy models per `postgresql/*` and `sqlalchemy/*`:

- Tables: `users`, `patients`, `doctors`, `appointments`
- Foreign-key relationships (patient ↔ appointment, doctor ↔ appointment)
- Table creation at startup (`Base.metadata.create_all`)

## Step 6 — Frontend / Code Generation

Generates a typed React + TypeScript + Vite frontend per `react/*`, `typescript/*`, `vite/*`:

- Components: Login, Dashboard, Patients, Doctors, Appointments
- A typed API service layer calling the generated FastAPI endpoints
- JWT stored and sent as a Bearer token

## Step 7 — Generated Web Application

The result is a runnable hospital-management web application whose frontend talks to its own
FastAPI backend over documented REST endpoints, backed by a PostgreSQL schema and JWT auth —
all consistent with the knowledge base's guidance.

## Key takeaway for the evaluator

The knowledge base does **not** store patient data. It stores **technical knowledge** that
keeps generated applications consistent, correct, and grounded in the documented stack. The
example above shows how a plain-English requirement is turned into a coherent technical
blueprint that every agent follows.
