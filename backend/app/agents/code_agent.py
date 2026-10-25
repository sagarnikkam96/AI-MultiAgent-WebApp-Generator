"""Code generation agent that coordinates full-stack project file creation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base_agent import BaseAgent
from ..code_generator.code_generator import PromptProvider
from ..project_writer.project_builder import ProjectBuilder
from ..language_catalog import output_language_instruction


class UserPromptProvider:
    """Provides prompt string to code generators."""

    def __init__(
        self,
        prompt: str,
        language: str = "en",
        design_context: dict[str, Any] | None = None,
    ) -> None:
        self.prompt = prompt
        self.language = language
        self.design_context = design_context

    def get_prompt(self) -> str:
        language_instruction = output_language_instruction(self.language)
        if self.design_context:
            return (
                f"{language_instruction}\n\n{self.prompt}\n\n"
                "Approved system design. Follow this design when generating the application:\n"
                f"{json.dumps(self.design_context, indent=2)}"
            )
        return f"{language_instruction}\n\n{self.prompt}"


class CodeGenerationAgent(BaseAgent):
    """Agent that translates requirements, plans, and blueprints into actual project files."""

    def __init__(self, name: str = "code_agent") -> None:
        super().__init__(name=name, description="Converts requirements and architecture plans into actual full-stack code")
        self.project_builder = ProjectBuilder()

    def analyze(self, user_prompt: str) -> Any:
        return user_prompt

    def generate(
        self,
        user_prompt: str,
        requirements: Any,
        base_path: str | Path | None = None,
        language: str = "en",
        design_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate actual frontend, backend, and database code files on disk."""
        project_name = getattr(requirements, "project_name", "Generated Project") or "Generated Project"
        if not base_path:
            base_path = Path(__file__).resolve().parents[2]

        prompt_provider: PromptProvider = UserPromptProvider(
            user_prompt,
            language=language,
            design_context=design_context,
        )

        created_paths = self.project_builder.build_and_write_project(
            project_name=project_name,
            prompt_provider=prompt_provider,
            base_path=base_path,
            requirements=requirements,
            language=language,
        )

        project_root = Path(base_path).resolve()
        relative_paths = [
            str(path.relative_to(project_root)).replace("\\", "/")
            for path in created_paths
        ]

        project_slug: str | None = None
        project_path: str | None = None
        for rel in relative_paths:
            parts = rel.split("/")
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
