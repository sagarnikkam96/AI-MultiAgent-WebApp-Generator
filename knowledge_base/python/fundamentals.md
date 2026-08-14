# Python — Fundamentals

Concise guidance on modern Python used by generated backends.

## Version and environment

- Target a recent Python version (3.10+).
- Use `from __future__ import annotations` to make annotations lazy and forward-compatible.
- Prefer environment isolation (`venv`) and a pinned `requirements.txt` per project.

## Typing

- Use type hints on function signatures and class attributes.
- Prefer built-in generics in Python 3.9+: `list[str]`, `dict[str, int]`, `tuple[int, ...]`.
- Use `Optional[X]` or `X | None` (Python 3.10+) for nullable values.
- Use `Any` sparingly; narrow types where practical.

## Style

- Follow PEP 8 naming: `snake_case` functions/variables, `CamelCase` classes, `UPPER_CASE` constants.
- Keep functions small and single-purpose.
- Use docstrings to explain contract ("what/why"), not mechanics.

## Errors

- Catch specific exceptions, not bare `except:`.
- Raise meaningful exceptions with clear messages.
- Let exceptions propagate to the framework's error handler when appropriate.

## Data handling

- Prefer `pathlib.Path` over string paths.
- Prefer dataclasses or Pydantic models over ad-hoc dicts for structured data.
- Use `json` with explicit encoding (`utf-8`).

Example:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    id: int
    name: str
    price: float | None = None
```
