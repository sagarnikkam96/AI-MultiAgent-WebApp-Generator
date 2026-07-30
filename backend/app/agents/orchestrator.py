"""Multi-agent orchestration for requirement-to-blueprint generation."""

from __future__ import annotations

from typing import Any

from .backend_agent import BackendGenerationAgent
from .database_agent import DatabaseGenerationAgent
from .planner_agent import PlannerAgent
from .requirement_agent import RequirementAgent


class MultiAgentOrchestrator:
    """Coordinates the end-to-end generation workflow for a web application."""

    def __init__(self) -> None:
        """Initialize all generation agents used in the workflow."""
        self.requirement_agent = RequirementAgent()
        self.planner_agent = PlannerAgent()
        self.backend_agent = BackendGenerationAgent()
        self.database_agent = DatabaseGenerationAgent()

    def run(self, user_prompt: str) -> dict[str, Any]:
        """Run the complete multi-agent workflow for the provided prompt."""
        requirements = self.requirement_agent.analyze(user_prompt)
        project_plan = self.planner_agent.plan(requirements)
        backend_blueprint = self.backend_agent.generate(project_plan)
        database_blueprint = self.database_agent.generate(requirements)

        return {
            "requirements": requirements,
            "project_plan": project_plan,
            "backend_blueprint": backend_blueprint,
            "database_blueprint": database_blueprint,
        }
