from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from app.agents.testing_agent import TestingAgent
from app.code_generator.project_slug import project_slug
from app.project_writer.file_writer import FileWriter
from app.project_writer.project_builder import ProjectBuilder


class PromptProvider:
    def __init__(self, prompt: str) -> None:
        self.prompt = prompt

    def get_prompt(self) -> str:
        return self.prompt


class GeneratedProjectValidationTests(unittest.TestCase):
    def test_project_builder_generates_backend_inside_shared_project_and_passes_validation(self) -> None:
        project_name = "An MyDigitalSpace"
        prompt = "Create a task management app with login, tasks, and reports."
        project_slug_value = project_slug(project_name)

        with tempfile.TemporaryDirectory() as temporary_dir:
            files = ProjectBuilder().build_project(project_name, PromptProvider(prompt)).files
            FileWriter(temporary_dir).write_files(files)

            generated_project_dir = Path(temporary_dir) / "generated_projects" / project_slug_value
            backend_files = list((generated_project_dir / "backend").rglob("*.py"))
            report = TestingAgent().test_project(generated_project_dir)
            backend_dir = generated_project_dir / "backend"
            app_dir = backend_dir / "app"
            app_package_exists = (app_dir / "__init__.py").is_file()
            requirements_file_exists = (backend_dir / "requirements.txt").is_file()
            import_result = subprocess.run(
                [sys.executable, "-c", "import app.main"],
                cwd=backend_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            for python_file in app_dir.rglob("*.py"):
                module = ast.parse(python_file.read_text(encoding="utf-8"))
                for imported in ast.walk(module):
                    if not isinstance(imported, ast.ImportFrom) or not imported.module:
                        continue
                    if not imported.module.startswith("app."):
                        continue
                    target = app_dir.joinpath(*imported.module.split(".")[1:])
                    self.assertTrue(
                        target.with_suffix(".py").is_file() or (target / "__init__.py").is_file(),
                        f"Unresolvable generated import in {python_file}: {imported.module}",
                    )

        self.assertTrue(backend_files, "Generated project should contain backend Python files")
        self.assertTrue(report.is_valid, report.logs)
        self.assertFalse(any("No Python files found" in error for error in report.errors))
        self.assertTrue(app_package_exists)
        self.assertTrue(requirements_file_exists)
        self.assertEqual(import_result.returncode, 0, import_result.stderr)


if __name__ == "__main__":
    unittest.main()
