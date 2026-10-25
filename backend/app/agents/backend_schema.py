"""Pydantic schema for backend blueprint generation."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class BackendEndpoint(BaseModel):
    """Specification for an individual API endpoint."""

    method: str = Field(..., description="HTTP Method (GET, POST, PUT, DELETE)")
    path: str = Field(..., description="Endpoint path (e.g. /api/items)")
    description: str = Field(..., description="Purpose of the endpoint")
    request_schema: str | None = Field(default=None, description="Request body Pydantic schema")
    response_schema: str = Field(default="dict", description="Response Pydantic schema")


class BackendBlueprint(BaseModel):
    """Structured backend blueprint for a generated web application."""

    framework: str = Field(..., description="Backend framework name (e.g. FastAPI)")
    folders: list[str] = Field(default_factory=list, description="Project folders for backend structure")
    api_modules: list[str] = Field(default_factory=list, description="API modules to be implemented")
    authentication: str = Field(..., description="Authentication strategy")
    database_integration: str = Field(..., description="Database integration approach")
    language: str = Field(default="en", description="Output language for API messages")

    endpoints: list[BackendEndpoint] = Field(default_factory=list, description="Detailed API route specifications")
    business_services: list[str] = Field(default_factory=list, description="Core business logic service layers")
    schemas: list[str] = Field(default_factory=list, description="Pydantic models for validation")
    cors_policy: dict[str, Any] = Field(default_factory=dict, description="CORS configuration details")
