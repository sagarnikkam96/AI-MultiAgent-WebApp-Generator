"""Planner agent that converts analyzed requirements into a project execution plan."""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent
from .planner_schema import ProjectPlan


class PlannerAgent(BaseAgent):
    """Agent that transforms requirement analysis into a concrete project plan."""

    def __init__(self, name: str = "planner_agent") -> None:
        """Initialize the planner agent."""
        super().__init__(name=name, description="Creates a project execution plan from requirements")

    def analyze(self, user_prompt: str) -> ProjectPlan:
        """Analyze a prompt or requirements-like input and return a project plan."""
        return self.plan(user_prompt)

    def plan(self, requirements: Any) -> ProjectPlan:
        """Create a project execution plan based on the provided requirements."""
        frontend = getattr(requirements, "frontend", "")
        backend = getattr(requirements, "backend", "")
        database = getattr(requirements, "database", "")
        project_name = getattr(requirements, "project_name", "Generated Project")

        frontend_tasks: list[str] = []
        backend_tasks: list[str] = []
        database_tasks: list[str] = []
        deployment_tasks: list[str] = ["Docker", "GitHub", "Render"]

        if frontend == "React":
            frontend_tasks = [
                "Create React Project",
                "Configure Routing",
                "Build Components",
                "API Integration",
            ]

        if backend == "FastAPI":
            backend_tasks = [
                "Create API",
                "Authentication",
                "Business Logic",
            ]

        if database == "PostgreSQL":
            database_tasks = [
                "Design Tables",
                "Relationships",
                "Seed Data",
            ]

        return ProjectPlan(
            project_name=project_name,
            frontend_tasks=frontend_tasks,
            backend_tasks=backend_tasks,
            database_tasks=database_tasks,
            deployment_tasks=deployment_tasks,
        )
