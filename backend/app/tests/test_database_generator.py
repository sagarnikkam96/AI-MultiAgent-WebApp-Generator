from __future__ import annotations

import ast
import unittest

from app.code_generator.database_generator import DatabaseGenerator


class DatabaseGeneratorIntegrationTests(unittest.TestCase):
    def test_build_database_files_avoids_backend_conflicts(self) -> None:
        prompt = "Build a task management application using React FastAPI PostgreSQL with login and tasks."
        generator = DatabaseGenerator()

        generated_files = generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())
        project_slug = generator._project_slug(prompt)
        paths = [generated_file.path for generated_file in generated_files]

        self.assertNotIn(f"generated_projects/{project_slug}/backend/database/models.py", paths)
        self.assertNotIn(f"generated_projects/{project_slug}/backend/database/session.py", paths)
        self.assertIn(f"generated_projects/{project_slug}/backend/database/base.py", paths)

        for generated_file in generated_files:
            if generated_file.path.endswith(".py"):
                ast.parse(generated_file.content)


if __name__ == "__main__":
    unittest.main()
