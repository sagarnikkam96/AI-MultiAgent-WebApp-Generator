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
                path=f"{project_root}/database/base.py",
                content=self._database_base_placeholder(),
            ),
        ]

    def _project_slug(self, requirements: str) -> str:
        text = requirements.lower()
        text = re.sub(r"[^a-z0-9\s-]", " ", text)
        text = re.sub(
            r"\b(build|create|generate|develop|design|application|app|system|using|with|and|or|for|the|a|an|react|fastapi|postgres|postgresql|login|signup|register|authentication|auth|jwt|token|users|user|patients|doctors|billing|products|cart|orders)\b",
            " ",
            text,
        )
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return "generated_project"

        words = [self._normalize_slug_word(word) for word in text.split()]
        unique_words: list[str] = []
        seen: set[str] = set()
        for word in words:
            if not word or word in seen:
                continue
            seen.add(word)
            unique_words.append(word)

        slug = "_".join(unique_words[:4])
        return slug[:50].strip("_") or "generated_project"

    def _normalize_slug_word(self, word: str) -> str:
        normalized = word.lower()
        singular_map = {
            "tasks": "task",
            "todos": "todo",
            "users": "user",
            "products": "product",
            "orders": "order",
            "carts": "cart",
            "appointments": "appointment",
            "categories": "category",
            "patients": "patient",
            "doctors": "doctor",
            "notes": "note",
            "posts": "post",
            "messages": "message",
            "invoices": "invoice",
        }
        return singular_map.get(normalized, normalized)

    def _database_base_placeholder(self) -> str:
        """Return a lightweight SQLAlchemy base module."""
        return (
            "from sqlalchemy.orm import declarative_base\n"
            "\n"
            "Base = declarative_base()\n"
        )
