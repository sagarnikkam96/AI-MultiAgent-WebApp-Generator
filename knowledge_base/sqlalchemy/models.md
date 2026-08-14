# SQLAlchemy — Models

Defining ORM models for the generated backend with SQLAlchemy.

## Declarative base

All models inherit from a shared declarative `Base`:

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

## A simple model

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(120), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

## Relationships

```python
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="appointments")


User.appointments = relationship("Appointment", back_populates="user")
```

- Map foreign keys with `ForeignKey("table.column")`.
- Use `relationship(...)` to traverse between models in queries.

## Column options

- `nullable=False` for required columns.
- `unique=True` for unique constraints.
- `server_default` for server-side defaults.
- `index=True` to add an index on frequently-queried columns.

## Table creation

Create all tables from metadata with:

```python
Base.metadata.create_all(bind=engine)
```

The generated backend runs this at startup so tables exist before serving requests.

## Constraints

Add `UniqueConstraint` or `CheckConstraint` in `__table_args__` for combined/complex rules.
Keep model definitions declarative and aligned with the intended PostgreSQL schema.
