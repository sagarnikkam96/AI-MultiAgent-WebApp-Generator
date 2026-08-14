# FastAPI — Request & Response

Handling request bodies, validation, and response shaping in FastAPI.

## Request models

Define request bodies with Pydantic `BaseModel`. FastAPI validates automatically and
returns a `422 Unprocessable Entity` on invalid input.

```python
from pydantic import BaseModel, Field


class NewUser(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    age: int = Field(..., ge=0, le=150)
```

## Response models

Use `response_model=` to guarantee the response shape and document it:
- Prevents leaking internal fields (e.g. hashed passwords).
- Enables automatic OpenAPI documentation.

Use `response_model_exclude_unset=True` or `exclude_none` to trim optional fields when desired.

## Status codes

- `201 Created` for successful resource creation.
- `204 No Content` for successful deletes/updates that return nothing.
- `200 OK` for reads and updates that return a body.
- Raise `HTTPException(status_code, detail)` for 4xx/5xx errors.

```python
from fastapi import HTTPException

if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

## Error shape

Keep error responses consistent. Use a common error schema when a standardised shape is
needed:

```json
{ "detail": "User not found" }
```

## Query parameters

Declare optional/required query params as function arguments with defaults. Use `Query(...)`
to add constraints such as `ge`, `le`, `min_length`.

## Serialisation

- Use `model_dump()` (Pydantic v2) to convert models to dicts for storage.
- Use `model_dump_json()` for JSON output where needed.
