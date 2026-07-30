"""Pydantic schema for backend blueprint generation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BackendBlueprint(BaseModel):
    """Structured backend blueprint for a generated web application."""

    framework: str = Field(..., description="Backend framework name")
    folders: list[str] = Field(default_factory=list, description="Project folders for backend structure")
    api_modules: list[str] = Field(default_factory=list, description="API modules to be implemented")
    authentication: str = Field(..., description="Authentication strategy")
    database_integration: str = Field(..., description="Database integration approach")
