# FastAPI — API Design

Guidance for building clean, consistent REST APIs with FastAPI.

## Principles

- Prefer **resource-oriented** endpoints (`/items`, `/items/{id}`) over action-style paths.
- Use HTTP methods correctly: GET (read), POST (create), PUT/PATCH (update), DELETE (remove).
- Return the correct HTTP status codes (200 OK, 201 Created, 204 No Content, 400/404/422, etc.).
- Validate all inputs explicitly with Pydantic models.

## Core building blocks

- **Path parameters** for resource identity, **query parameters** for filtering/pagination.
- **Request body** via Pydantic `BaseModel` schemas.
- **Response models** to document and shape output; `response_model=` enforces shape.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class ItemIn(BaseModel):
    name: str
    price: float


class ItemOut(ItemIn):
    id: int


app = FastAPI()

ITEMS: dict[int, ItemOut] = {}


@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(payload: ItemIn) -> ItemOut:
    item = ItemOut(id=len(ITEMS) + 1, **payload.model_dump())
    ITEMS[item.id] = item
    return item
```

## Versioning and consistency

- Keep response shapes consistent across endpoints for the same resource.
- Use one canonical schema per resource (input vs. output variants).
- Document endpoints with FastAPI's auto-generated OpenAPI docs (`/docs`).

## Separation

- Keep routes thin: validate in the route, delegate business logic to a service layer.
- Group related routes into routers and include them in the main app.
