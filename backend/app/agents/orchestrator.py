"""Multi-agent orchestration for requirement-to-project generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .backend_agent import BackendGenerationAgent
from .database_agent import DatabaseGenerationAgent
from .planner_agent import PlannerAgent
from .requirement_agent import RequirementAgent

from ..code_generator.code_generator import PromptProvider
from ..llm.ollama_client import OllamaClient
from ..project_writer.project_builder import ProjectBuilder


class UserPromptProvider:
    """Provides the original user prompt to the code generators."""

    def __init__(self, prompt: str) -> None:
        self.prompt = prompt

    def get_prompt(self) -> str:
        return self.prompt


class MultiAgentOrchestrator:
    """Coordinates the end-to-end generation workflow for a web application."""

    def __init__(self) -> None:
        """Initialize all generation agents and the project builder."""
        self.requirement_agent = RequirementAgent()
        self.planner_agent = PlannerAgent()
        self.backend_agent = BackendGenerationAgent()
        self.database_agent = DatabaseGenerationAgent()
        self.ollama_client = OllamaClient()
        self.project_builder = ProjectBuilder()

    def _serialize(self, value: Any) -> Any:
        """Serialize Pydantic models and other values into JSON-safe structures."""
        if isinstance(value, BaseModel):
            return value.model_dump()

        if isinstance(value, dict):
            return {
                key: self._serialize(item)
                for key, item in value.items()
            }

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
            "Review the structured application generation results and provide "
            "a concise summary. Focus on the requirements, project plan, "
            "backend blueprint, and database blueprint.\n\n"
            f"Requirements:\n{json.dumps(requirements_data, indent=2)}\n\n"
            f"Project Plan:\n{json.dumps(project_plan_data, indent=2)}\n\n"
            f"Backend Blueprint:\n{json.dumps(backend_blueprint_data, indent=2)}\n\n"
            f"Database Blueprint:\n{json.dumps(database_blueprint_data, indent=2)}"
        )

    def _get_project_name(self, requirements: Any) -> str:
        """Get the project name from the requirement analysis."""

        if isinstance(requirements, BaseModel):
            project_name = getattr(
                requirements,
                "project_name",
                "Generated Project",
            )
        elif isinstance(requirements, dict):
            project_name = requirements.get(
                "project_name",
                "Generated Project",
            )
        else:
            project_name = getattr(
                requirements,
                "project_name",
                "Generated Project",
            )

        if not project_name:
            return "Generated Project"

        return str(project_name)

    def _generate_project(self, user_prompt: str, requirements: Any) -> dict[str, Any]:
        """Generate the actual frontend, backend, and database project files."""

        project_name = self._get_project_name(requirements)

        prompt_provider: PromptProvider = UserPromptProvider(user_prompt)

        project_root = Path(__file__).resolve().parents[2]

        created_paths = self.project_builder.build_and_write_project(
            project_name=project_name,
            prompt_provider=prompt_provider,
            base_path=project_root,
        )

        relative_paths = [
            str(path.relative_to(project_root))
            for path in created_paths
        ]

        # Derive the generated project slug (e.g. "hospital_management_appointment")
        # from the on-disk location so the frontend can download/build/preview it.
        project_slug: str | None = None
        project_path: str | None = None
        for relative_path in relative_paths:
            parts = relative_path.replace("\\", "/").split("/")
            if len(parts) >= 2 and parts[0] == "generated_projects":
                project_slug = parts[1]
                project_path = f"generated_projects/{project_slug}"
                break

        return {
            "project_name": project_name,
            "project_slug": project_slug,
            "project_path": project_path,
            "files_created": relative_paths,
            "files_count": len(created_paths),
        }

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
            ollama_response = self.ollama_client.generate(
                ollama_prompt
            )
        except RuntimeError as error:
            ollama_response = f"Ollama integration failed: {error}"

        generated_project: dict[str, Any] = {}

        try:
            generated_project = self._generate_project(
                user_prompt,
                requirements,
            )
        except Exception as error:
            generated_project = {
                "project_name": self._get_project_name(requirements),
                "files_created": [],
                "files_count": 0,
                "error": str(error),
            }

        return {
            "requirements": self._serialize(requirements),
            "project_plan": self._serialize(project_plan),
            "backend_blueprint": self._serialize(backend_blueprint),
            "database_blueprint": self._serialize(database_blueprint),
            "ollama_response": ollama_response,
            "generated_project": generated_project,
        }