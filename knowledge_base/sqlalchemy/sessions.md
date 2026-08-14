# SQLAlchemy — Sessions

Managing database sessions in the generated FastAPI backend.

## Engine

Create one engine per app and reuse it. Example PostgreSQL connection:

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/app_db"
engine = create_engine(DATABASE_URL)
```

## Session factory

Create a sessionmaker bound to the engine:

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
```

## FastAPI dependency

Expose a `get_db` dependency that yields a session and always closes it:

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from .session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Use it in routes:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()
```

## Transaction handling

- `db.add(obj)` stages an insert/update.
- `db.commit()` persists the transaction.
- `db.rollback()` undoes on error.
- `db.refresh(obj)` re-loads database-generated values (e.g. auto-increment id).

```python
db.add(user)
db.commit()
db.refresh(user)
```

## Querying

```python
users = db.query(User).filter(User.active == True).all()          # noqa: E712
user = db.query(User).filter(User.id == 1).first()
items = db.query(Item).order_by(Item.created_at.desc()).limit(20).all()
```

## Important rules

- Never share a session across requests.
- Always close the session (the `get_db` dependency handles it).
- Use the same engine for `create_all` and the request sessions so tables and queries agree.
