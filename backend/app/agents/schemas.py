"""Pydantic schemas for agent request and response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Generic request payload for an agent."""

    prompt: str = Field(..., description="User prompt or instruction")
    context: str | None = Field(default=None, description="Optional context")


class AgentResponse(BaseModel):
    """Generic response payload returned by an agent."""

    result: str = Field(..., description="Agent result")
    success: bool = Field(default=True, description="Whether the agent completed successfully")


class RequirementSchema(BaseModel):
    """Structured schema for analyzed project requirements."""

    project_name: str = Field(..., description="Name of the project")
    project_type: str = Field(default="", description="Type of the project")
    frontend: str = Field(..., description="Frontend technology")
    backend: str = Field(..., description="Backend technology")
    database: str = Field(..., description="Database technology")
    authentication: bool = Field(default=False, description="Whether authentication is required")
    modules: list[str] = Field(default_factory=list, description="Planned modules")
    validation_errors: list[str] = Field(default_factory=list, description="Validation issues found")


class RequirementInput(BaseModel):
    """Input schema for requirement analysis."""

    project_name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Project description")
    constraints: list[str] = Field(default_factory=list, description="Project constraints")


class RequirementOutput(BaseModel):
    """Output schema for requirement analysis."""

    summary: str = Field(..., description="Summary of the analyzed requirements")
    features: list[str] = Field(default_factory=list, description="Extracted features")
    risks: list[str] = Field(default_factory=list, description="Potential risks")
