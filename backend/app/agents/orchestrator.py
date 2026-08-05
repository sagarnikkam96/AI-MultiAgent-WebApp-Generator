"""Multi-agent orchestration for requirement-to-blueprint generation."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from .backend_agent import BackendGenerationAgent
from .database_agent import DatabaseGenerationAgent
from .planner_agent import PlannerAgent
from .requirement_agent import RequirementAgent
from ..llm.ollama_client import OllamaClient


class MultiAgentOrchestrator:
    """Coordinates the end-to-end generation workflow for a web application."""

    def __init__(self) -> None:
        """Initialize all generation agents used in the workflow."""
        self.requirement_agent = RequirementAgent()
        self.planner_agent = PlannerAgent()
        self.backend_agent = BackendGenerationAgent()
        self.database_agent = DatabaseGenerationAgent()
        self.ollama_client = OllamaClient()

    def _serialize(self, value: Any) -> Any:
        """Serialize Pydantic models and other values into JSON-safe structures."""
        if isinstance(value, BaseModel):
            return value.model_dump()
        if isinstance(value, dict):
            return {key: self._serialize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._serialize(item) for item in value]
        if isinstance(value, tuple):
            return [self._serialize(item) for item in value]
        return value

    def _build_ollama_prompt(
        self,
        requirements: Any,
        project_plan: Any,
        backend_blueprint: Any,
        database_blueprint: Any,
    ) -> str:
        """Build a concise prompt to summarize structured generation results."""
        requirements_data = self._serialize(requirements)
        project_plan_data = self._serialize(project_plan)
        backend_blueprint_data = self._serialize(backend_blueprint)
        database_blueprint_data = self._serialize(database_blueprint)

        return (
            "Review the structured application generation results and provide a concise summary. "
            "Focus on the requirements, project plan, backend blueprint, and database blueprint.\n\n"
            f"Requirements:\n{json.dumps(requirements_data, indent=2)}\n\n"
            f"Project Plan:\n{json.dumps(project_plan_data, indent=2)}\n\n"
            f"Backend Blueprint:\n{json.dumps(backend_blueprint_data, indent=2)}\n\n"
            f"Database Blueprint:\n{json.dumps(database_blueprint_data, indent=2)}"
        )

    def run(self, user_prompt: str) -> dict[str, Any]:
        """Run the complete multi-agent workflow for the provided prompt."""
        requirements = self.requirement_agent.analyze(user_prompt)
        project_plan = self.planner_agent.plan(requirements)
        backend_blueprint = self.backend_agent.generate(project_plan)
        database_blueprint = self.database_agent.generate(requirements)

        ollama_prompt = self._build_ollama_prompt(
            requirements,
            project_plan,
            backend_blueprint,
            database_blueprint,
        )

        try:
            ollama_response = self.ollama_client.generate(ollama_prompt)
        except RuntimeError as error:
            ollama_response = f"Ollama integration failed: {error}"

        return {
            "requirements": requirements,
            "project_plan": project_plan,
            "backend_blueprint": backend_blueprint,
            "database_blueprint": database_blueprint,
            "ollama_response": ollama_response,
        }
