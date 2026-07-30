"""Database generation agent for creating database blueprints."""

from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent
from .database_schema import DatabaseBlueprint


class DatabaseGenerationAgent(BaseAgent):
    """Agent that creates a database blueprint from project requirements."""

    def __init__(self, name: str = "database_generation_agent") -> None:
        """Initialize the database generation agent."""
        super().__init__(name=name, description="Generates a database blueprint from project requirements")

    def analyze(self, user_prompt: str) -> Any:
        """Analyze a user prompt and return the input as-is."""
        return user_prompt

    def generate(self, requirements: Any) -> DatabaseBlueprint:
        """Generate a database blueprint from the provided requirements."""
        database_type = getattr(requirements, "database", "")

        if database_type == "PostgreSQL":
            return DatabaseBlueprint(
                database_type="PostgreSQL",
                tables=["Users", "Roles", "Doctors", "Patients", "Appointments", "Billing"],
                relationships=[
                    "Users -> Roles",
                    "Doctors -> Appointments",
                    "Patients -> Appointments",
                    "Patients -> Billing",
                ],
                indexes=["users_email_idx", "appointments_date_idx"],
            )

        return DatabaseBlueprint(
            database_type=database_type or "PostgreSQL",
            tables=["Users", "Roles", "Doctors", "Patients", "Appointments", "Billing"],
            relationships=[
                "Users -> Roles",
                "Doctors -> Appointments",
                "Patients -> Appointments",
                "Patients -> Billing",
            ],
            indexes=["users_email_idx", "appointments_date_idx"],
        )
