from __future__ import annotations

from pathlib import Path

from ..code_generator.backend_generator import BackendGenerator
from ..code_generator.code_schema import GeneratedProject, GeneratedFile
from ..code_generator.database_generator import DatabaseGenerator
from ..code_generator.frontend_generator import FrontendGenerator
from ..code_generator.code_generator import PromptProvider
from .file_writer import FileWriter


class ProjectBuilder:
    """Builds a generated project from multiple code generators."""

    def __init__(
        self,
        frontend_generator: FrontendGenerator | None = None,
        backend_generator: BackendGenerator | None = None,
        database_generator: DatabaseGenerator | None = None,
    ) -> None:
        self.frontend_generator = frontend_generator or FrontendGenerator()
        self.backend_generator = backend_generator or BackendGenerator()
        self.database_generator = database_generator or DatabaseGenerator()

    def build_project(self, project_name: str, prompt_provider: PromptProvider) -> GeneratedProject:
        """Combine frontend, backend, and database files into a generated project."""
        files: list[GeneratedFile] = []
        files.extend(self.frontend_generator.generate_files(prompt_provider))
        files.extend(self.backend_generator.generate_files(prompt_provider))
        files.extend(self.database_generator.generate_files(prompt_provider))
        return GeneratedProject(project_name=project_name, files=files)

    def build_and_write_project(
        self,
        project_name: str,
        prompt_provider: PromptProvider,
        base_path: str | Path,
    ) -> list[Path]:
        """Build the generated project and write files to disk."""
        generated_project = self.build_project(project_name, prompt_provider)
        file_writer = FileWriter(base_path)
        return file_writer.write_files(generated_project.files)
