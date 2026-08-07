from __future__ import annotations

from pydantic import BaseModel


class GeneratedFile(BaseModel):
    """Represents a single generated source file."""

    path: str
    content: str


class GeneratedProject(BaseModel):
    """Represents a generated project bundle."""

    project_name: str
    files: list[GeneratedFile]
