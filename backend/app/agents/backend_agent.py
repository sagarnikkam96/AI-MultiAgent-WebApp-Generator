"""Backend generation agent for creating backend development blueprints."""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent
from .backend_schema import BackendBlueprint


class BackendGenerationAgent(BaseAgent):
    """Agent that creates a backend blueprint from a project plan."""

    def __init__(self, name: str = "backend_generation_agent") -> None:
        """Initialize the backend generation agent."""
        super().__init__(name=name, description="Generates a backend blueprint from a project plan")

    def analyze(self, user_prompt: str) -> Any:
        """Analyze a user prompt and return the input as-is."""
        return user_prompt

    def generate(self, plan: Any) -> BackendBlueprint:
        """Generate a backend blueprint for the provided project plan."""
        backend_framework = getattr(plan, "backend", "")

        if backend_framework == "FastAPI":
            return BackendBlueprint(
                framework="FastAPI",
                folders=["api", "models", "services", "database", "auth", "routers"],
                api_modules=["Authentication", "Users", "Dashboard"],
                authentication="JWT",
                database_integration="SQLAlchemy",
            )

        return BackendBlueprint(
            framework=backend_framework or "FastAPI",
            folders=["api", "models", "services", "database", "auth", "routers"],
            api_modules=["Authentication", "Users", "Dashboard"],
            authentication="JWT",
            database_integration="SQLAlchemy",
        )
