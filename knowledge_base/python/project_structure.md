# Python — Project Structure

Recommended layout for a generated FastAPI + SQLAlchemy backend.

## Directory layout

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── api/                    # Router aggregation (endpoints)
│   ├── config/                 # Settings / environment config
│   ├── database/               # Engine + session + base
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic
│   ├── routers/                # Route modules (or inside api/)
│   └── auth/                   # Authentication / JWT helpers
├── requirements.txt
└── .env                        # Secrets / config (git-ignored)
```

## Layering rules

- **API layer** (`routers`, `api/`): define HTTP endpoints and validation via schemas.
- **Service layer** (`services/`): business logic; keeps routes thin.
- **Data layer** (`models/`, `database/`): ORM models, engine, sessions.
- Dependencies flow downward: routers → services → models/database.
- Do not import routers from models; keep the dependency direction acyclic.

## Configuration

- Centralise configuration in one settings module (e.g. Pydantic `BaseSettings`).
- Keep secrets in `.env`, never hard-code them.

## Startup / lifespan

- Create engine and tables at startup using an async lifespan context manager.
- Always `Base.metadata.create_all(bind=engine)` (or migrations) before serving traffic.

This structure keeps generated backends consistent, testable, and easy to navigate.
