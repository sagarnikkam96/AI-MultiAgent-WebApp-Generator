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

        project_name = self._extract_project_name(prompt)
        project_type = self._detect_project_type(prompt)
        frontend = self._detect_frontend(prompt)
        backend = self._detect_backend(prompt)
        database = self._detect_database(prompt)
        authentication = self._detect_authentication(prompt)
        modules = self._detect_modules(prompt)

        validation_errors: list[str] = []
        if not frontend:
            validation_errors.append("Frontend technology not specified")
        if not backend:
            validation_errors.append("Backend technology not specified")
        if not project_name:
            validation_errors.append("Project name not detected")

        return RequirementSchema(
            project_name=project_name,
            project_type=project_type,
            frontend=frontend,
            backend=backend,
            database=database,
            authentication=authentication,
            modules=modules,
            validation_errors=validation_errors,
        )

    def _extract_project_name(self, prompt: str) -> str:
        """Extract a project name using simple keyword matching."""
        if "project name" in prompt:
            extracted = prompt.split("project name", 1)[1].strip()
            for separator in (" for ", " is ", " called ", " using ", " with ", "\n"):
                if separator in extracted:
                    extracted = extracted.split(separator, 1)[0].strip()
                    break
            return extracted.strip()

        if "called" in prompt:
            extracted = prompt.split("called", 1)[1].strip()
            for separator in (" for ", " is ", " with ", "\n"):
                if separator in extracted:
                    extracted = extracted.split(separator, 1)[0].strip()
                    break
            return extracted.strip()

        return ""

    def _detect_project_type(self, prompt: str) -> str:
        """Detect the project domain type from common keywords."""
        project_type_map: dict[str, str] = {
            "hospital": "Healthcare",
            "shopping": "E-Commerce",
            "ecommerce": "E-Commerce",
            "e-commerce": "E-Commerce",
            "school": "Education",
            "hotel": "Hospitality",
            "banking": "Finance",
        }

        for keyword, project_type in project_type_map.items():
            if keyword in prompt:
                return project_type

        return ""

    def _detect_frontend(self, prompt: str) -> str:
        """Detect a frontend technology from the prompt."""
        if "react" in prompt:
            return "React"
        return ""

    def _detect_backend(self, prompt: str) -> str:
        """Detect a backend technology from the prompt."""
        if "fastapi" in prompt:
            return "FastAPI"
        if "django" in prompt:
            return "Django"
        if "flask" in prompt:
            return "Flask"
        return ""

    def _detect_database(self, prompt: str) -> str:
        """Detect a database technology from the prompt."""
        if "postgresql" in prompt:
            return "PostgreSQL"
        if "mysql" in prompt:
            return "MySQL"
        if "mongodb" in prompt:
            return "MongoDB"
        return "No database specified"

    def _detect_authentication(self, prompt: str) -> bool:
        """Determine whether authentication is required."""
        return any(keyword in prompt for keyword in ("authentication", "login", "jwt"))

    def _detect_modules(self, prompt: str) -> list[str]:
        """Detect module names using simple keyword matching."""
        modules: list[str] = []
        module_keywords: list[tuple[str, tuple[str, ...]]] = [
            ("Login", ("login",)),
            ("Dashboard", ("dashboard",)),
            ("Admin", ("admin",)),
            ("Patients", ("patients",)),
            ("Doctors", ("doctors",)),
            ("Billing", ("billing",)),
            ("Products", ("products",)),
            ("Orders", ("orders",)),
            ("Cart", ("cart",)),
        ]

        for module_name, keywords in module_keywords:
            if any(keyword in prompt for keyword in keywords):
                modules.append(module_name)

        return modules
