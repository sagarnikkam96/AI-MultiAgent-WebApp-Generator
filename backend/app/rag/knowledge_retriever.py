"""RAG Knowledge Retriever for Multi-Agent Generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class KnowledgeRetriever:
    """Retrieves contextual architecture patterns and templates from the knowledge base and datasets."""

    def __init__(self, workspace_root: Path | None = None) -> None:
        if workspace_root is None:
            self.root = Path(__file__).resolve().parents[3]
        else:
            self.root = workspace_root

        self.knowledge_dir = self.root / "knowledge_base"
        self.dataset_dir = self.root / "dataset"
        self._templates_cache: dict[str, Any] | None = None

    def _load_templates(self) -> dict[str, Any]:
        if self._templates_cache is not None:
            return self._templates_cache

        templates_file = self.dataset_dir / "web_templates.json"
        if templates_file.is_file():
            try:
                self._templates_cache = json.loads(templates_file.read_text(encoding="utf-8"))
                return self._templates_cache or {}
            except Exception:
                pass
        return {}

    def find_domain_template(self, prompt: str) -> dict[str, Any] | None:
        """Find matching domain template from dataset for the user prompt."""
        templates_data = self._load_templates()
        domains = templates_data.get("domains", [])
        prompt_lower = prompt.lower()

        for domain in domains:
            keywords = domain.get("keywords", [])
            if any(k in prompt_lower for k in keywords):
                return domain

        return domains[0] if domains else None

    def get_architecture_guidelines(self, domain: str) -> list[str]:
        """Retrieve best practice guidelines for the given domain."""
        return [
            "Use React 18 with TypeScript functional components and hooks",
            "Implement full CRUD state management with mock persistence",
            "Provide responsive CSS layout with modern dark/light styling",
            "Ensure accessible ARIA attributes and keyboard navigation",
            "Structure backend with FastAPI APIRouter and Pydantic schemas",
            "Include comprehensive SQLite / PostgreSQL database models",
        ]
