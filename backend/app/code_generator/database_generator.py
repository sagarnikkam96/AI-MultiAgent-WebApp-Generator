from __future__ import annotations

import re
from typing import Protocol

from .code_generator import CodeGenerator, PromptProvider
from .code_schema import GeneratedFile


class DatabaseGenerator(CodeGenerator):
    """Generates database code artifacts for Version 2."""

    def generate_files(self, prompt_provider: PromptProvider) -> list[GeneratedFile]:
        """Create database files from the given prompt provider."""
        prompt = prompt_provider.get_prompt()
        return self._build_database_files(prompt)

    def _build_database_files(self, prompt: str) -> list[GeneratedFile]:
        """Construct the initial database file list."""
        project_slug = self._project_slug(prompt)
        project_root = f"generated_projects/{project_slug}/backend"
        return [
            GeneratedFile(
                path=f"{project_root}/database/models.py",
                content=self._database_models_placeholder(),
            ),
            GeneratedFile(
                path=f"{project_root}/database/session.py",
                content=self._database_session_placeholder(),
            ),
        ]

    def _project_slug(self, requirements: str) -> str:
        text = requirements.lower()
        text = re.sub(r"[^a-z0-9\s-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return "generated_project"
        slug = "_".join(text.split()[:4])
        return slug[:50].strip("_") or "generated_project"

    def _database_models_placeholder(self) -> str:
        """Return a placeholder SQLAlchemy models file."""
        return (
            "from sqlalchemy import Column, Integer, String\n"
            "from sqlalchemy.ext.declarative import declarative_base\n"
            "\n"
            "Base = declarative_base()\n"
            "\n"
            "class User(Base):\n"
            "    __tablename__ = 'users'\n"
            "    id = Column(Integer, primary_key=True, index=True)\n"
            "    name = Column(String, nullable=False)\n"
        )

    def _database_session_placeholder(self) -> str:
        """Return a placeholder SQLAlchemy session file."""
        return (
            "from sqlalchemy import create_engine\n"
            "from sqlalchemy.orm import sessionmaker\n"
            "\n"
            "DATABASE_URL = 'postgresql://user:password@localhost:5432/database'\n"
            "engine = create_engine(DATABASE_URL)\n"
            "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
        )
