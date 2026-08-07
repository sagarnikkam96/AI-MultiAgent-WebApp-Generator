from __future__ import annotations

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
        # TODO: implement database generation using Ollama and structured prompts
        return [
            GeneratedFile(
                path="backend/app/database/models.py",
                content=self._database_models_placeholder(),
            ),
            GeneratedFile(
                path="backend/app/database/session.py",
                content=self._database_session_placeholder(),
            ),
        ]

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
