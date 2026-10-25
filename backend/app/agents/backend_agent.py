"""Backend generation agent for creating domain-specific backend development blueprints."""

from __future__ import annotations

import re
from typing import Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from .backend_schema import BackendBlueprint, BackendEndpoint
from ..code_generator.website_spec import detect_website_key, PROJECT_TYPE_MODULES


class BackendGenerationAgent(BaseAgent):
    """Agent that creates a domain-specific backend blueprint from a project plan or requirements."""

    def __init__(self, name: str = "backend_generation_agent") -> None:
        """Initialize the backend generation agent."""
        super().__init__(name=name, description="Generates a domain-specific backend blueprint from a project plan")

    def analyze(self, user_prompt: str) -> Any:
        """Analyze a user prompt and return the input as-is."""
        return user_prompt

    def generate(self, plan: Any) -> BackendBlueprint:
        """Generate a backend blueprint for the provided project plan or requirements."""
        backend_framework = getattr(plan, "backend", "FastAPI") or "FastAPI"
        language = getattr(plan, "language", "en") or "en"
        project_name = getattr(plan, "project_name", "") or ""

        # Extract domain key
        domain_context = " ".join(
            [
                project_name,
                str(getattr(plan, "project_type", "") or ""),
                str(getattr(plan, "purpose", "") or ""),
                " ".join(str(item) for item in (getattr(plan, "modules", None) or [])),
            ]
        )
        domain_key = detect_website_key(domain_context)
        domain_modules = PROJECT_TYPE_MODULES.get(domain_key, ["Records", "Items", "Reports"])

        # Determine domain-specific API modules
        api_modules: list[str] = ["Auth", "Dashboard"]
        for mod in domain_modules[:4]:
            if mod not in api_modules and mod != "Dashboard":
                api_modules.append(mod)

        endpoints: list[BackendEndpoint] = [
            BackendEndpoint(
                method="GET",
                path="/",
                description="Root health and greeting endpoint",
                request_schema=None,
                response_schema="dict",
            ),
            BackendEndpoint(
                method="GET",
                path="/health",
                description="Liveness and database connectivity health probe",
                request_schema=None,
                response_schema="dict",
            ),
            BackendEndpoint(
                method="POST",
                path="/api/login",
                description="User login and JWT token generation",
                request_schema="LoginRequest",
                response_schema="TokenResponse",
            ),
        ]

        for mod in domain_modules[:3]:
            slug = mod.lower()
            model_name = mod[:-1] if mod.endswith("s") else mod
            endpoints.extend([
                BackendEndpoint(
                    method="GET",
                    path=f"/api/{slug}",
                    description=f"List and search all {mod.lower()} records with pagination",
                    request_schema=None,
                    response_schema=f"list[{model_name}Response]",
                ),
                BackendEndpoint(
                    method="POST",
                    path=f"/api/{slug}",
                    description=f"Create a new {model_name.lower()} record with validation",
                    request_schema=f"{model_name}Create",
                    response_schema=f"{model_name}Response",
                ),
                BackendEndpoint(
                    method="GET",
                    path=f"/api/{slug}/{{id}}",
                    description=f"Retrieve a specific {model_name.lower()} record by ID",
                    request_schema=None,
                    response_schema=f"{model_name}Response",
                ),
                BackendEndpoint(
                    method="PUT",
                    path=f"/api/{slug}/{{id}}",
                    description=f"Update fields of an existing {model_name.lower()} record",
                    request_schema=f"{model_name}Update",
                    response_schema=f"{model_name}Response",
                ),
                BackendEndpoint(
                    method="DELETE",
                    path=f"/api/{slug}/{{id}}",
                    description=f"Delete a {model_name.lower()} record by ID",
                    request_schema=None,
                    response_schema="dict",
                ),
            ])

        business_services = [
            f"{mod}Service: Handles data validation, database persistence, and queries for {mod.lower()}"
            for mod in domain_modules[:4]
        ]
        business_services.insert(0, "AuthService: Password hashing with bcrypt, JWT token creation, and role verification")

        schemas = ["TokenResponse", "LoginRequest", "UserResponse", "UserCreate"]
        for mod in domain_modules[:4]:
            model_name = mod[:-1] if mod.endswith("s") else mod
            schemas.extend([f"{model_name}Base", f"{model_name}Create", f"{model_name}Update", f"{model_name}Response"])

        cors_policy = {
            "allow_origins": ["*"],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

        return BackendBlueprint(
            framework=backend_framework or "FastAPI",
            folders=["api", "models", "services", "database", "auth", "routers", "schemas"],
            api_modules=api_modules,
            authentication="JWT with bcrypt password hashing",
            database_integration="SQLAlchemy with SQLite / PostgreSQL",
            language=language,
            endpoints=endpoints,
            business_services=business_services,
            schemas=schemas,
            cors_policy=cors_policy,
        )
