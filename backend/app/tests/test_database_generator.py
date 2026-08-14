from __future__ import annotations

import ast
import unittest

from app.code_generator.backend_generator import BackendGenerator
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

    def test_backend_generator_uses_same_postgres_config_for_connection_and_session(self) -> None:
        prompt = "Build a task management application using React FastAPI PostgreSQL with login and tasks."
        generator = BackendGenerator()

        generated_files = generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())
        connection_file = next(file for file in generated_files if file.path.endswith("database/connection.py"))
        session_file = next(file for file in generated_files if file.path.endswith("database/session.py"))

        self.assertIn("postgresql://postgres:postgres@localhost:5432/app_db", connection_file.content)
        self.assertIn("postgresql://postgres:postgres@localhost:5432/app_db", session_file.content)
        self.assertNotIn("sqlite:///./app.db", session_file.content)

    def test_backend_generator_uses_postgresql_for_database_modules(self) -> None:
        prompt = "Build a task management application using React FastAPI PostgreSQL with login and tasks."
        generator = BackendGenerator()

        generated_files = generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())
        connection_file = next(file for file in generated_files if file.path.endswith("database/connection.py"))
        session_file = next(file for file in generated_files if file.path.endswith("database/session.py"))

        self.assertIn("postgresql://postgres:postgres@localhost:5432/app_db", connection_file.content)
        self.assertIn("postgresql://postgres:postgres@localhost:5432/app_db", session_file.content)
        self.assertNotIn("sqlite:///./app.db", connection_file.content)
        self.assertNotIn("sqlite:///./app.db", session_file.content)


    def test_backend_generator_emits_requirements_txt_with_postgres(self) -> None:
        prompt = "Build a task management application using React FastAPI PostgreSQL with login and tasks."
        generator = BackendGenerator()

        generated_files = generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())
        project_slug = generator._project_slug(prompt)
        requirements_file = next(file for file in generated_files if file.path.endswith("requirements.txt"))

        self.assertEqual(
            requirements_file.path,
            f"generated_projects/{project_slug}/backend/requirements.txt",
        )
        for dependency in ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "psycopg2-binary"]:
            self.assertIn(dependency, requirements_file.content)

    def test_backend_generator_requirements_without_postgres(self) -> None:
        prompt = "Build a notes application using React FastAPI with login and notes."
        generator = BackendGenerator()

        generated_files = generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())
        requirements_file = next(file for file in generated_files if file.path.endswith("requirements.txt"))

        for dependency in ["fastapi", "uvicorn", "sqlalchemy", "pydantic"]:
            self.assertIn(dependency, requirements_file.content)
        self.assertNotIn("psycopg2-binary", requirements_file.content)


    def test_backend_generator_wires_table_creation_at_startup(self) -> None:
        prompt = "Build a task management application using React FastAPI PostgreSQL with login and tasks."
        generator = BackendGenerator()

        generated_files = generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())
        main_file = next(file for file in generated_files if file.path.endswith("main.py"))
        models_file = next(file for file in generated_files if file.path.endswith("models/models.py"))
        connection_file = next(file for file in generated_files if file.path.endswith("database/connection.py"))

        # The generated app must execute create_all on startup using a lifespan.
        self.assertIn("Base.metadata.create_all(bind=engine)", main_file.content)
        self.assertIn("lifespan=lifespan", main_file.content)
        self.assertIn("@asynccontextmanager", main_file.content)
        # create_all must use the same engine the application session uses.
        self.assertIn("from database.connection import engine", main_file.content)
        # create_all must use the same Base the generated models inherit from.
        self.assertIn("from models.models import Base", main_file.content)
        self.assertIn("Base = declarative_base()", models_file.content)
        self.assertIn("engine = create_engine(", connection_file.content)

        for generated_file in generated_files:
            if generated_file.path.endswith(".py"):
                ast.parse(generated_file.content)

    def test_backend_generator_main_without_database_has_no_table_creation(self) -> None:
        prompt = "Build an app using FastAPI"
        generator = BackendGenerator()

        generated_files = generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())
        main_file = next(file for file in generated_files if file.path.endswith("main.py"))

        self.assertNotIn("create_all", main_file.content)
        self.assertNotIn("database.connection", main_file.content)
        self.assertNotIn("models.models", main_file.content)
        self.assertNotIn("lifespan", main_file.content)


    def test_backend_generator_adds_cors_for_react_frontend(self) -> None:
        prompt = "Build a task management application using React FastAPI PostgreSQL with login and tasks."
        generator = BackendGenerator()

        generated_files = generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())
        main_file = next(file for file in generated_files if file.path.endswith("main.py"))

        self.assertIn("from fastapi.middleware.cors import CORSMiddleware", main_file.content)
        self.assertIn("CORSMiddleware", main_file.content)
        self.assertIn("app.add_middleware(", main_file.content)
        self.assertIn("allow_origins", main_file.content)
        self.assertIn("http://localhost:5173", main_file.content)
        self.assertIn("http://127.0.0.1:5173", main_file.content)
        self.assertIn("allow_credentials=True", main_file.content)
        self.assertIn("allow_methods", main_file.content)
        self.assertIn("allow_headers", main_file.content)


if __name__ == "__main__":
    unittest.main()
