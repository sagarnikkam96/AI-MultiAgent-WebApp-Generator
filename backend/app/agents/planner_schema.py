"""Pydantic schema for project planning output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectPlan(BaseModel):
    """Structured execution plan for a generated web application."""

    project_name: str = Field(..., description="Name of the project")
    frontend_tasks: list[str] = Field(default_factory=list, description="Frontend implementation tasks")
    backend_tasks: list[str] = Field(default_factory=list, description="Backend implementation tasks")
    database_tasks: list[str] = Field(default_factory=list, description="Database implementation tasks")
    deployment_tasks: list[str] = Field(default_factory=list, description="Deployment tasks")
