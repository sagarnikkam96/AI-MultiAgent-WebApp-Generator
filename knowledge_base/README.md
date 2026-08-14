# Curated Software Development Knowledge Base

**Name:** Curated Software Development Knowledge Base

**Type:** Curated technical knowledge/document collection for AI-assisted software generation

## Purpose

This knowledge base provides focused, reliable technical context for the AI system when
it generates web applications. It is a **curated** collection of technical documentation —
it is **not** an external dataset and it is **not** sourced from Kaggle, UCI, Hugging Face,
GitHub, or any other external dataset. The content is hand-written, intentionally concise,
and scoped to the exact technology stack this generator produces.

The knowledge base exists so that the multi-agent pipeline can ground its decisions in
accurate, consistent technical guidance for:

- **Python** — language fundamentals and project structure
- **FastAPI** — API design, routing, request/response handling
- **React** — components and state management
- **TypeScript** — types and interfaces
- **Vite** — project setup and build
- **PostgreSQL** — database design and queries
- **SQLAlchemy** — models and sessions
- **REST API** — principles and endpoint design
- **Authentication / JWT** — token-based auth and authorization
- **Web Security** — web and API security practices
- **Database Design** — relational modelling guidance
- **Software Architecture** — backend and frontend architecture
- **Development Patterns** — reusable software-development patterns

## How the collection is organised

```
knowledge_base/
├── README.md
├── RAG_INTEGRATION.md          # Future / planned retrieval integration point
├── python/
├── fastapi/
├── react/
├── typescript/
├── vite/
├── postgresql/
├── sqlalchemy/
├── rest_api/
├── authentication/
├── security/
├── architecture/
├── patterns/
└── demonstration/              # Safe, non-sensitive example scenarios
```

## Current status

- RAG / vector search is **NOT yet implemented** in the project.
- This knowledge base is a **planned retrieval source** for a future RAG pipeline.
- See [`RAG_INTEGRATION.md`](RAG_INTEGRATION.md) for the proposed (future) integration point.
- The example in `demonstration/` is purely illustrative. It contains **no** real or
  sensitive data — no real names, medical records, phone numbers, or addresses.

## How to use

1. Read the topic folders for the relevant technology (e.g. `fastapi/` for API guidance).
2. Use `demonstration/hospital_management.md` as a worked example of how technical context
   maps to the agent pipeline.
3. When RAG is implemented, this collection's Markdown files (or their embeddings) would be
   the retrieval source consulted during requirement analysis and planning.
