"""Multi-agent orchestration for autonomous full-stack web application generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .backend_agent import BackendGenerationAgent
from .backend_schema import BackendBlueprint
from .code_agent import CodeGenerationAgent
from .database_agent import DatabaseGenerationAgent
from .database_schema import DatabaseBlueprint
from .debugging_agent import DebuggingAgent
from .deployment_agent import DeploymentAgent
from .planner_agent import PlannerAgent
from .planner_schema import ProjectPlan
from .requirement_agent import RequirementAgent
from .security_agent import SecurityAgent
from .testing_agent import TestingAgent
from .schemas import RequirementSchema

from ..llm.hybrid_model import HybridModelEngine
from ..llm.ollama_client import OllamaClient
from ..project_writer.project_builder import ProjectBuilder
from ..rag.knowledge_retriever import KnowledgeRetriever


class MultiAgentOrchestrator:
    """Coordinates the end-to-end 9-agent autonomous generation workflow."""

    def __init__(self) -> None:
        """Initialize all generation, testing, security, and deployment agents."""
        self.requirement_agent = RequirementAgent()
        self.planner_agent = PlannerAgent()
        self.backend_agent = BackendGenerationAgent()
        self.database_agent = DatabaseGenerationAgent()
        self.code_agent = CodeGenerationAgent()
        self.testing_agent = TestingAgent()
        self.debugging_agent = DebuggingAgent()
        self.security_agent = SecurityAgent()
        self.deployment_agent = DeploymentAgent()

        self.ollama_client = OllamaClient()
        self.hybrid_engine = HybridModelEngine()
        self.knowledge_retriever = KnowledgeRetriever()
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
        """Build a prompt to summarize structured multi-agent generation results."""
        requirements_data = self._serialize(requirements)
        project_plan_data = self._serialize(project_plan)
        backend_blueprint_data = self._serialize(backend_blueprint)
        database_blueprint_data = self._serialize(database_blueprint)

        return (
            "Review the structured multi-agent application generation results and provide "
            "a concise architectural summary. Focus on the requirements, project plan, "
            "backend blueprint, and database blueprint.\n\n"
            f"Requirements:\n{json.dumps(requirements_data, indent=2)}\n\n"
            f"Project Plan:\n{json.dumps(project_plan_data, indent=2)}\n\n"
            f"Backend Blueprint:\n{json.dumps(backend_blueprint_data, indent=2)}\n\n"
            f"Database Blueprint:\n{json.dumps(database_blueprint_data, indent=2)}"
        )

    def _get_project_name(self, requirements: Any) -> str:
        """Get the project name from the requirement analysis."""
        if isinstance(requirements, BaseModel):
            project_name = getattr(requirements, "project_name", "Generated Project")
        elif isinstance(requirements, dict):
            project_name = requirements.get("project_name", "Generated Project")
        else:
            project_name = getattr(requirements, "project_name", "Generated Project")

        return str(project_name or "Generated Project")

    def _get_language(self, requirements: Any) -> str:
        """Extract the detected language from requirement analysis."""
        if isinstance(requirements, BaseModel):
            return getattr(requirements, "language", "en") or "en"
        if isinstance(requirements, dict):
            return requirements.get("language", "en") or "en"
        return getattr(requirements, "language", "en") or "en"

    def plan_sdlc(self, user_prompt: str, language: str = "en") -> dict[str, Any]:
        """Create the reviewable requirements and technical design for an SDLC run."""
        requirements = self.requirement_agent.analyze(user_prompt)
        requirements.language = language or requirements.language
        project_plan = self.planner_agent.plan(requirements)
        backend_blueprint = self.backend_agent.generate(project_plan)
        database_blueprint = self.database_agent.generate(requirements)

        return {
            "srs": {
                "project_name": requirements.project_name,
                "purpose": requirements.purpose,
                "scope": requirements.features or requirements.modules,
                "stakeholders": requirements.user_roles,
                "functional_requirements": requirements.functional_requirements,
                "non_functional_requirements": requirements.constraints,
                "data_requirements": requirements.data_requirements,
                "acceptance_criteria": [
                    f"The application supports {feature.lower()}."
                    for feature in requirements.features
                ],
            },
            "requirements": self._serialize(requirements),
            "project_plan": self._serialize(project_plan),
            "backend_blueprint": self._serialize(backend_blueprint),
            "database_blueprint": self._serialize(database_blueprint),
        }

    def run(
        self,
        user_prompt: str,
        language: str = "en",
        requirements: RequirementSchema | None = None,
        project_plan: ProjectPlan | None = None,
        backend_blueprint: BackendBlueprint | None = None,
        database_blueprint: DatabaseBlueprint | None = None,
    ) -> dict[str, Any]:
        """Run the complete autonomous workflow in the requested output language."""
        project_root = Path(__file__).resolve().parents[2]

        # 1. Requirement Agent
        requirements = requirements or self.requirement_agent.analyze(user_prompt)
        requirements.language = language or requirements.language

        # 2. Design / Planning Agent
        project_plan = project_plan or self.planner_agent.plan(requirements)

        # 3. Backend Agent
        backend_blueprint = backend_blueprint or self.backend_agent.generate(project_plan)

        # 4. Database Agent
        database_blueprint = database_blueprint or self.database_agent.generate(requirements)

        # Extract attributes for summary and narration
        project_name = self._get_project_name(requirements)
        project_type = getattr(requirements, "project_type", "Web Application") or "Web Application"
        modules = getattr(requirements, "modules", []) or ["Core Module", "Dashboard"]
        frontend = getattr(requirements, "frontend", "React") or "React"
        backend = getattr(requirements, "backend", "FastAPI") or "FastAPI"
        database = getattr(requirements, "database", "PostgreSQL / SQLite") or "PostgreSQL / SQLite"

        # 5. Code Agent: Generate full-stack project files
        generated_project: dict[str, Any] = {}
        try:
            generated_project = self.code_agent.generate(
                user_prompt=user_prompt,
                requirements=requirements,
                base_path=project_root,
                language=language,
                design_context={
                    "project_plan": self._serialize(project_plan),
                    "backend_blueprint": self._serialize(backend_blueprint),
                    "database_blueprint": self._serialize(database_blueprint),
                },
            )
        except Exception as error:
            generated_project = {
                "project_name": project_name,
                "project_slug": None,
                "project_path": None,
                "files_created": [],
                "files_count": 0,
                "error": str(error),
            }

        # 6. Testing Agent & 7. Debugging Agent Loop
        project_slug = generated_project.get("project_slug")
        testing_report = None
        debug_report = None
        security_report = None
        deployment_report = None

        if project_slug:
            project_dir = project_root / "generated_projects" / project_slug
            if project_dir.is_dir():
                # Run Testing Suite
                initial_test = self.testing_agent.test_project(project_dir)
                # Run Debug / Repair Loop if errors found
                final_test, debug_res = self.debugging_agent.debug_loop(project_dir, initial_report=initial_test)
                testing_report = final_test
                debug_report = debug_res

                # 8. Security Agent: Automated Security Audit
                security_report = self.security_agent.audit_project(project_dir)

                # 9. Deployment Agent: Container & Production Configuration
                deployment_report = self.deployment_agent.prepare_deployment(project_dir, project_name=project_name)

        # LLM Architectural Summary
        ollama_prompt = self._build_ollama_prompt(
            requirements,
            project_plan,
            backend_blueprint,
            database_blueprint,
        )

        try:
            ollama_response = self.ollama_client.generate(ollama_prompt)
            if not ollama_response or ollama_response.startswith("Ollama integration failed"):
                ollama_response = self.hybrid_engine.generate_summary(
                    project_name=project_name,
                    project_type=project_type,
                    modules=modules,
                    frontend=frontend,
                    backend=backend,
                    database=database,
                )
        except Exception:
            ollama_response = self.hybrid_engine.generate_summary(
                project_name=project_name,
                project_type=project_type,
                modules=modules,
                frontend=frontend,
                backend=backend,
                database=database,
            )

        narration_script = self.hybrid_engine.generate_narration_script(
            project_name=project_name,
            project_type=project_type,
            modules=modules,
            frontend=frontend,
            backend=backend,
            database=database,
        )

        return {
            "requirements": self._serialize(requirements),
            "project_plan": self._serialize(project_plan),
            "backend_blueprint": self._serialize(backend_blueprint),
            "database_blueprint": self._serialize(database_blueprint),
            "generated_project": generated_project,
            "testing_report": self._serialize(testing_report) if testing_report else None,
            "debug_report": self._serialize(debug_report) if debug_report else None,
            "security_report": self._serialize(security_report) if security_report else None,
            "deployment_report": self._serialize(deployment_report) if deployment_report else None,
            "ollama_response": ollama_response,
            "narration_script": narration_script,
            "language": language,
        }