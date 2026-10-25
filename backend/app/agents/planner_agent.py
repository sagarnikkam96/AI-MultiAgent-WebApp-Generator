"""Planner agent that converts analyzed requirements into a comprehensive project execution plan."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from .planner_schema import ProjectPlan
from ..code_generator.website_spec import detect_website_key, derive_website_spec
from ..language_catalog import LANGUAGE_NAMES


class PlannerAgent(BaseAgent):
    """Agent that transforms requirement analysis into a concrete, domain-specific project plan."""

    def __init__(self, name: str = "planner_agent") -> None:
        """Initialize the planner agent."""
        super().__init__(name=name, description="Creates a project execution plan from requirements")

    def analyze(self, user_prompt: str) -> ProjectPlan:
        """Analyze a prompt or requirements-like input and return a project plan."""
        return self.plan(user_prompt)

    def plan(self, requirements: Any) -> ProjectPlan:
        """Create a project execution plan based on the provided requirements."""
        if isinstance(requirements, str):
            from .requirement_agent import RequirementAgent
            requirements = RequirementAgent().analyze(requirements)

        frontend = getattr(requirements, "frontend", "React") or "React"
        backend = getattr(requirements, "backend", "FastAPI") or "FastAPI"
        database = getattr(requirements, "database", "PostgreSQL / SQLite") or "PostgreSQL / SQLite"
        project_name = getattr(requirements, "project_name", "Generated Project") or "Generated Project"
        project_type = getattr(requirements, "project_type", "Web Application") or "Web Application"
        language = getattr(requirements, "language", "en") or "en"
        modules = getattr(requirements, "modules", []) or ["Dashboard", "Records"]
        user_roles = getattr(requirements, "user_roles", []) or ["Administrator", "User"]
        supported_languages = ", ".join(LANGUAGE_NAMES.values())

        spec = derive_website_spec(project_name, project_name=project_name)
        domain_key = detect_website_key(project_name)

        # 1. Tasks for backwards compatibility
        frontend_tasks = [
            f"Initialize {frontend} 18 + TypeScript + Vite project",
            "Configure responsive CSS styling tokens and dark/light themes",
            f"Implement navigation bar with language switcher ({language})",
            *[f"Build {m} view component with interactive state" for m in modules[:4]],
            "Integrate REST API client for backend communication",
        ]

        backend_tasks = [
            f"Initialize {backend} application with CORS middleware",
            "Define Pydantic v2 schemas for request and response validation",
            "Implement SQLAlchemy ORM database models and relationships",
            *[f"Create CRUD router for {m.lower()} endpoint" for m in modules[:3] if m not in ("Login", "Dashboard")],
            "Configure authentication and token verification",
        ]

        database_tasks = [
            f"Design {database} relational schema",
            "Define primary keys, foreign keys, and indexes",
            "Implement automatic table migration and startup creation",
            "Generate initial sample seed records for immediate testing",
        ]

        deployment_tasks = [
            "Generate multi-stage Dockerfile for FastAPI backend",
            "Generate Nginx static container Dockerfile for React frontend",
            "Create docker-compose.yml for full-stack orchestration",
            "Generate production .env.example configuration",
        ]

        # 2. Detailed architectural plan
        system_architecture = (
            f"Three-tier full-stack architecture comprising a responsive {frontend} SPA client, "
            f"a high-concurrency asynchronous {backend} REST API service, and a {database} relational data store."
        )

        frontend_architecture = [
            "React 18 single-page application with modular functional components and React Hooks",
            "TypeScript type safety across models, API responses, and UI props",
            "Vanilla CSS modern design system with CSS custom properties (variables) for dark/light themes",
            f"Dynamic multilingual dictionary provider supporting {supported_languages}",
            "Client-side modal management, interactive state management, and real-time search filtering",
        ]

        backend_architecture = [
            "FastAPI asynchronous REST application with Starlette routing and lifespan management",
            "Pydantic v2 request body validation and response serialization schemas",
            "Modular APIRouter separation for domain entities, authentication, and health checks",
            "SQLAlchemy ORM session management with context-manager dependency injection",
            "Cross-Origin Resource Sharing (CORS) security configuration for frontend origins",
        ]

        database_architecture = [
            "SQLAlchemy declarative base with relational table mappings",
            "Support for zero-dependency SQLite local runtime and scalable PostgreSQL production",
            "One-to-Many and Many-to-One relationship cascades and foreign key constraints",
            "Performance indexing on searchable fields (email, names, timestamps, foreign keys)",
        ]

        pages = [
            "Dashboard: Live metrics cards, recent activity stream, quick actions, and data summary",
            *[f"{m}: Dedicated view for managing {m.lower()} records and inspecting details" for m in modules if m != "Dashboard"],
        ]

        components = [
            "AppShell: Header brand, language switcher, theme toggle, and navigation tabs",
            "MetricsGrid: Domain KPI stat cards with trend indicators",
            "DataTable: Searchable, sortable table with status badges and action triggers",
            "RecordModal: Form modal for creating and updating domain records",
            "AudioNarrator: Voice project speaker with speech synthesis playback",
            "LiveSimulator: In-browser interactive preview simulator",
        ]

        navigation = ["Dashboard", *[m for m in modules if m != "Dashboard"]]

        forms = [
            f"Create {modules[0] if modules else 'Record'} Form (validation, submit, feedback)",
            "Search & Filter Form (instant search bar with category filters)",
            "User Authentication Form (sign in / sign up with email and password)",
        ]

        tables = [
            f"{m} Records Table with Name, Category/Type, Status, and Timestamp columns"
            for m in modules[:3] if m != "Dashboard"
        ]
        if not tables:
            tables = ["Domain Records Table with Title, Status, and Created Date"]

        apis = [
            "GET /health - Service health status check",
            "POST /api/login - Authentication token generation",
            *[f"GET /api/{m.lower()} - List {m.lower()} records" for m in modules[:3] if m not in ("Login", "Dashboard")],
            *[f"POST /api/{m.lower()} - Create new {m.lower()} record" for m in modules[:3] if m not in ("Login", "Dashboard")],
            *[f"DELETE /api/{m.lower()}/{{id}} - Delete {m.lower()} record" for m in modules[:2] if m not in ("Login", "Dashboard")],
        ]

        user_workflow = [
            f"1. User navigates to {project_name} and views domain KPI overview on Dashboard.",
            f"2. User selects a display language from the supported set: {supported_languages}.",
            f"3. User clicks 'Create New' to open the domain-specific entry modal and adds a new record.",
            f"4. Application validates inputs on frontend, transmits payload to FastAPI backend, and saves in database.",
            f"5. Real-time data table updates instantly with the new record, and feedback notification appears.",
            f"6. User can filter, search, inspect, or manage items across dedicated module tabs.",
        ]

        ui_ux_structure = (
            "Modern glassmorphism and cyberpunk-inspired aesthetic with rich contrast, curated HSL color tokens, "
            "smooth micro-interactions, responsive grid layouts, and seamless dark/light mode switching."
        )

        return ProjectPlan(
            project_name=project_name,
            frontend_tasks=frontend_tasks,
            backend_tasks=backend_tasks,
            database_tasks=database_tasks,
            deployment_tasks=deployment_tasks,
            language=language,
            system_architecture=system_architecture,
            frontend_architecture=frontend_architecture,
            backend_architecture=backend_architecture,
            database_architecture=database_architecture,
            pages=pages,
            components=components,
            navigation=navigation,
            forms=forms,
            tables=tables,
            apis=apis,
            user_workflow=user_workflow,
            ui_ux_structure=ui_ux_structure,
        )
