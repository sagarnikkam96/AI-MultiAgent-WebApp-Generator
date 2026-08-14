# FastAPI — Routing

How to structure and register routes with FastAPI routers.

## Using `APIRouter`

Group related endpoints into a router and include it in the app:

```python
# app/routers/items.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.items import ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)) -> list[ItemOut]:
    return db.query(ItemOut).all()
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import items

app = FastAPI()
app.include_router(items.router)
```

## Route naming conventions

- Use plural resource nouns for collection routes: `/users`, `/orders`.
- Nest sub-resources when the dependency is strong: `/users/{user_id}/orders`.
- Use `{resource_id}` (singular) for individual resource paths.
- Keep URLs lowercase; separate words with hyphens.

## Path vs. query parameters

- Path parameters identify a specific resource (`/users/42`).
- Query parameters filter, sort, or paginate a collection (`/users?role=admin&page=2`).

## Depends and dependency injection

- Use `Depends` for shared dependencies (DB sessions, current-user, auth).
- FastAPI resolves dependencies automatically and handles cleanup.

## Order matters

- Define static paths before parameterised ones where they could conflict
  (`/users/me` before `/users/{user_id}`) to avoid shadowing.
