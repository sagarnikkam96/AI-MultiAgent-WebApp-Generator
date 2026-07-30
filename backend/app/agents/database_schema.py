"""Pydantic schema for database blueprint generation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DatabaseBlueprint(BaseModel):
    """Structured database blueprint for a generated web application."""

    database_type: str = Field(..., description="Database system type")
    tables: list[str] = Field(default_factory=list, description="Database tables to be created")
    relationships: list[str] = Field(default_factory=list, description="Table relationships")
    indexes: list[str] = Field(default_factory=list, description="Database indexes")
