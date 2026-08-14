# Patterns — Software Development Patterns

Reusable software-development patterns that apply to generated full-stack applications.

## Repository pattern (data access)

Encapsulate data access behind a repository/service so routes do not touch SQL directly.
This keeps data logic in one place and easy to test.

```python
class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()
```

## Dependency injection (DI)

Pass dependencies (DB session, current user, services) into functions rather than
instantiating them inside. FastAPI's `Depends` provides this natively and improves
testability.

## Layered / N-tier pattern

Separate presentation (routes), business logic (services), and persistence (models). See
`architecture/backend_architecture.md`. This keeps each layer focused and replaceable.

## Factory pattern

Create objects (e.g. code generators, agents) through a factory/registry when you need
consistent construction with configuration.

## Strategy pattern

Select an algorithm/behaviour at runtime. Useful for the multi-agent pipeline where each
agent implements the same interface (`BaseAgent.analyze`) but with different logic.

## Facade pattern

Expose a simplified interface over a complex subsystem. The `MultiAgentOrchestrator` is a
facade over the requirement/planner/backend/database agents and the project builder — callers
only interact with `orchestrator.run(prompt)`.

## DTO / schema pattern

Use dedicated data-transfer objects (Pydantic schemas) to decouple API contracts from the
underlying models. Validate input and shape output explicitly.

## Error-handling pattern

Centralise error handling so the API returns consistent error responses and logs details
server-side without leaking internals.

## Rules of thumb

- Prefer composition over inheritance.
- Keep interfaces small and explicit.
- Make units small, focused, and testable.
- Favour simple, working code over speculative abstraction.
