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
    language: str = Field(default="en", description="Output language for generated content")

    system_architecture: str = Field(default="", description="High-level multi-tier system architecture")
    frontend_architecture: list[str] = Field(default_factory=list, description="Frontend layers and state management")
    backend_architecture: list[str] = Field(default_factory=list, description="Backend REST routers and service layers")
    database_architecture: list[str] = Field(default_factory=list, description="Relational data models and persistence")
    pages: list[str] = Field(default_factory=list, description="Planned frontend pages/views")
    components: list[str] = Field(default_factory=list, description="Planned reusable UI components")
    navigation: list[str] = Field(default_factory=list, description="Navigation menu items")
    forms: list[str] = Field(default_factory=list, description="Input forms to be generated")
    tables: list[str] = Field(default_factory=list, description="Data tables to be generated")
    apis: list[str] = Field(default_factory=list, description="Planned REST API endpoints")
    user_workflow: list[str] = Field(default_factory=list, description="Step-by-step user interaction workflow")
    ui_ux_structure: str = Field(default="", description="UI/UX design principles and layout guidelines")
