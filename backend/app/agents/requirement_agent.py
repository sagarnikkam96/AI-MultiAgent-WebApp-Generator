"""Deterministic requirement analysis agent."""

from __future__ import annotations

from .base_agent import BaseAgent
from .schemas import RequirementSchema


class RequirementAgent(BaseAgent):
    """Agent that extracts structured requirements from a prompt."""

    def __init__(self, name: str = "requirement_agent") -> None:
        """Initialize the requirement agent."""
        super().__init__(name=name, description="Extracts structured requirements from a prompt")

    def analyze(self, user_prompt: str) -> RequirementSchema:
        """Analyze a user prompt and return a structured requirement schema."""
        prompt = user_prompt.lower()

        frontend = "React" if "react" in prompt else "Plain HTML/CSS/JavaScript"
        backend = "FastAPI" if "fastapi" in prompt else "Node.js" if "node" in prompt else "Python"
        database = "PostgreSQL" if "postgresql" in prompt else "SQLite" if "sqlite" in prompt else "No database specified"

        authentication = any(
            keyword in prompt for keyword in ("authentication", "login", "signin", "sign in")
        )

        modules: list[str] = []
        if "dashboard" in prompt:
            modules.append("Dashboard")
        if "admin" in prompt:
            modules.append("Admin")
        if "profile" in prompt:
            modules.append("Profile")
        if "auth" in prompt or "login" in prompt:
            modules.append("Authentication")

        return RequirementSchema(
            project_name="Generated Project",
            frontend=frontend,
            backend=backend,
            database=database,
            authentication=authentication,
            modules=modules,
        )
