# Curated Software Development Knowledge Base — Dataset Documentation

This document describes the project's curated technical knowledge base, which serves as the
"dataset/knowledge base" for the AI Multi-Agent Web Application Generator.

## 1. Knowledge base name

**Curated Software Development Knowledge Base**

## 2. Knowledge base type

**Curated technical knowledge/document collection for AI-assisted software generation.**

It is a hand-curated collection of technical documents. It is **not** an external dataset and
is **not** sourced from Kaggle, UCI, Hugging Face, GitHub, or any other external dataset.
It contains **no** fabricated records or invented statistics — the content is real technical
guidance, written for this project's technology stack.

## 3. Why it is used

The knowledge base gives the AI system reliable, consistent technical context when generating
web applications. Instead of relying only on pattern-matching and prompt text, the pipeline
can consult grounded technical guidance for the exact stack it produces (Python, FastAPI,
React, TypeScript, Vite, PostgreSQL, SQLAlchemy, REST APIs, JWT, security, architecture, and
development patterns).

## 4. Categories

| Category                 | Documents                                                        |
| ------------------------ | ---------------------------------------------------------------- |
| Python                   | `python/fundamentals.md`, `python/project_structure.md`          |
| FastAPI                  | `fastapi/api_design.md`, `fastapi/routing.md`, `fastapi/request_response.md` |
| React                    | `react/components.md`, `react/state_management.md`               |
| TypeScript               | `typescript/types.md`, `typescript/interfaces.md`                |
| Vite                     | `vite/project_setup.md`, `vite/build.md`                         |
| PostgreSQL               | `postgresql/database_design.md`, `postgresql/queries.md`         |
| SQLAlchemy               | `sqlalchemy/models.md`, `sqlalchemy/sessions.md`                 |
| REST API                 | `rest_api/principles.md`, `rest_api/endpoints.md`                |
| Authentication / JWT     | `authentication/jwt.md`, `authentication/authorization.md`       |
| Web Security             | `security/web_security.md`, `security/api_security.md`           |
| Database Design          | covered under `postgresql/`                                      |
| Software Architecture    | `architecture/backend_architecture.md`, `architecture/frontend_architecture.md` |
| Development Patterns     | `patterns/software_patterns.md`                                  |

## 5. Data/document format

- **Format:** plain Markdown (`.md`) files, organised by topic folder.
- **Granularity:** one topic per file, with short sections and code examples.
- **Location:** `knowledge_base/` (see `knowledge_base/README.md`).
- Each document is concise, self-contained, and scoped to the generated technology stack.
- A `demonstration/` sub-folder holds a safe, illustrative example (no real/sensitive data).

## 6. How the AI system can use it

The knowledge base can be used in two ways:

1. **Direct prompt enrichment (current/planned):** relevant document content can be injected
   as "technical context" into agent prompts so the LLM and deterministic agents generate
   code that follows the documented conventions.
2. **Retrieval (future RAG):** once a retrieval step exists, the documents would be chunked,
   embedded, and retrieved based on the requirement keywords and agent-needs.

## 7. How it relates to RAG

> **RAG status: Planned / future — NOT currently implemented.**

The project does **not** yet have an RAG pipeline, vector database, or embedding model (see
`knowledge_base/RAG_INTEGRATION.md`). The knowledge base is a **prepared retrieval corpus**
for a future RAG step. As of now, the retrieval stage in the pipeline below is **planned
functionality**, **not** working functionality, and it is labelled as such.

## 8. How it supports the multi-agent architecture

The knowledge base provides consistent technical context to each agent:

- **Requirement Agent** — maps prompt keywords to a technology stack (React, FastAPI,
  PostgreSQL, JWT) that the knowledge base documents.
- **Planning Agent** — derives task lists aligned with the documented architecture.
- **Backend Agent** — follows `fastapi/*`, `rest_api/*`, and `authentication/*` guidance.
- **Database Agent** — follows `postgresql/*` and `sqlalchemy/*` guidance.
- **Frontend Generator** — follows `react/*`, `typescript/*`, and `vite/*` guidance.

It keeps the whole pipeline consistent: the frontend it generates talks to the backend it
generates, and both follow the same documented REST/JWT/PostgreSQL conventions.

## 9. How it helps application generation

- **Consistency:** every generated app follows the same documented, sound conventions.
- **Correctness:** grounded guidance reduces ad-hoc guesses about the stack.
- **Maintainability:** generated projects match the reference architectures documented here.
- **Demonstrability:** the worked example in `demonstration/` shows evaluators how technical
  context guides generation end-to-end.

## Conceptual pipeline

```
User Requirement
        ↓
Requirement Analysis
        ↓
Knowledge Retrieval / Technical Context   ← PLANNED (future RAG) — not yet wired in
        ↓
Planning Agent
        ↓
Backend Agent
        ↓
Database Agent
        ↓
Frontend/Code Generation
        ↓
Generated Web Application
```

> The "Knowledge Retrieval / Technical Context" stage is **planned/future** functionality.
> The existing, working pipeline (Requirement → Planning → Backend → Database → Frontend) is
> unchanged.
