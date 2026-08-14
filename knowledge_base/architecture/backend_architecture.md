# Architecture — Backend Architecture

Recommended backend architecture for generated FastAPI applications.

## Layered architecture

```
Route layer (FastAPI routers)
        ↓
Service layer (business logic)
        ↓
Data layer (SQLAlchemy models, sessions)
        ↓
PostgreSQL
```

- **Route layer**: thin HTTP handlers; parse/validate input, orchestrate the service layer,
  shape responses.
- **Service layer**: business rules and workflows; keeps routes readable and testable.
- **Data layer**: ORM models, engine, sessions.

## Separation of concerns

- Keep HTTP details (status codes, request/response schemas) in the route layer.
- Keep SQL/ORM in the data layer.
- Keep business decisions in the service layer.

## Dependency direction

Dependencies flow one way: routes → services → data. Avoid circular imports by placing
shared types/schemas in a common module.

## Configuration & lifecycle

- Centralise config in a settings module (Pydantic `BaseSettings`) loaded from environment.
- Set up the engine and create tables in a FastAPI lifespan at startup.
- Provide a `get_db` dependency for request-scoped sessions.

## Project layout

```
app/
├── main.py
├── config/        # settings
├── database/      # engine + session + base
├── models/        # ORM models
├── schemas/       # Pydantic schemas
├── services/      # business logic
└── routers/       # endpoint modules
```

## Testability

- Keep pure logic (services) independent of the HTTP layer for easy unit testing.
- Use dependency injection (FastAPI `Depends`) to substitute the DB in tests.
