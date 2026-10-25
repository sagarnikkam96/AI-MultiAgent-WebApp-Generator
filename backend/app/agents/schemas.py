"""Pydantic schemas for agent request and response models."""

from __future__ import annotations

from typing import Any
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
    language: str = Field(default="en", description="Detected or requested output language")
    purpose: str = Field(default="", description="High-level purpose and goal of the application")
    domain: str = Field(default="General", description="Specific business/application domain")
    user_roles: list[str] = Field(default_factory=list, description="Identified user roles (e.g. Admin, Customer, Staff)")
    features: list[str] = Field(default_factory=list, description="Extracted key features")
    pages: list[str] = Field(default_factory=list, description="Identified application pages and screens")
    functional_requirements: list[str] = Field(default_factory=list, description="Functional capabilities")
    data_requirements: list[str] = Field(default_factory=list, description="Identified domain entities and data items")
    constraints: list[str] = Field(default_factory=list, description="Project constraints and non-functional requirements")


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


class TestingCheck(BaseModel):
    """Result of an individual validation check."""

    name: str = Field(..., description="Name of the check")
    category: str = Field(default="general", description="Category (frontend, backend, database, structure)")
    passed: bool = Field(default=True, description="Whether the check passed")
    details: str = Field(default="", description="Detailed message or log")


class TestingReport(BaseModel):
    """Structured report produced by the Testing Agent."""

    is_valid: bool = Field(default=True, description="Overall test result")
    passed_count: int = Field(default=0, description="Total passed checks")
    failed_count: int = Field(default=0, description="Total failed checks")
    checks: list[TestingCheck] = Field(default_factory=list, description="List of performed checks")
    errors: list[str] = Field(default_factory=list, description="List of error messages detected")
    logs: str = Field(default="", description="Consolidated test output log")


class DebugFix(BaseModel):
    """Details of a code fix applied by the Debug Agent."""

    file_path: str = Field(..., description="File that was modified")
    issue_type: str = Field(..., description="Category of error fixed (syntax, import, missing_field, config)")
    root_cause: str = Field(..., description="Root cause identified")
    fix_description: str = Field(..., description="Summary of changes made")
    applied: bool = Field(default=True, description="Whether the fix was applied to disk")


class DebugReport(BaseModel):
    """Structured report produced by the Debug Agent."""

    attempts: int = Field(default=1, description="Number of debug iterations performed")
    succeeded: bool = Field(default=True, description="Whether all issues were resolved")
    fixes: list[DebugFix] = Field(default_factory=list, description="List of applied fixes")
    message: str = Field(default="", description="Summary message")
    remaining_blockers: list[str] = Field(default_factory=list, description="Any remaining issues if unresolved")


class SecurityVulnerability(BaseModel):
    """A detected security check issue or recommendation."""

    check_name: str = Field(..., description="Security check identifier")
    severity: str = Field(default="warning", description="Severity (info, warning, critical)")
    description: str = Field(..., description="Description of the security finding")
    file_path: str = Field(default="", description="Relevant file path")
    remediation: str = Field(default="", description="Remediation steps applied or recommended")
    remediated: bool = Field(default=True, description="Whether this issue is remediated in generated code")


class SecurityReport(BaseModel):
    """Structured report produced by the Security Agent."""

    is_secure: bool = Field(default=True, description="Overall security assessment")
    score: int = Field(default=100, description="Security score from 0 to 100")
    passed_checks: list[str] = Field(default_factory=list, description="List of passed security checks")
    vulnerabilities: list[SecurityVulnerability] = Field(default_factory=list, description="Security findings")
    summary: str = Field(default="", description="Overall security summary")


class DeploymentArtifact(BaseModel):
    """A deployment configuration file prepared by the Deployment Agent."""

    filename: str = Field(..., description="File name (e.g. Dockerfile, docker-compose.yml)")
    path: str = Field(..., description="Relative project path")
    description: str = Field(default="", description="Purpose of this artifact")


class DeploymentReport(BaseModel):
    """Structured report produced by the Deployment Agent."""

    ready: bool = Field(default=True, description="Whether deployment artifacts are prepared")
    artifacts: list[DeploymentArtifact] = Field(default_factory=list, description="Generated deployment files")
    environment_variables: list[str] = Field(default_factory=list, description="Required environment variables")
    instructions: str = Field(default="", description="Step-by-step deployment instructions")
    status_message: str = Field(default="", description="Status summary message")
