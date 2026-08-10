from __future__ import annotations

import sys
from pathlib import Path

# Ensure the local `app` package is importable when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.code_generator.backend_generator import BackendGenerator
from app.code_generator.frontend_generator import FrontendGenerator
from app.code_generator.code_schema import GeneratedFile
from app.project_writer.file_writer import FileWriter


def main() -> None:
    project_name = "Hospital Management System"
    file_writer = FileWriter(Path(__file__).resolve().parents[3])
    frontend_generator = FrontendGenerator()

    generation_tasks = [
        ("package.json", "Generate a valid React + TypeScript Vite package.json for a hospital management frontend project"),
        ("index.html", "Generate a Vite-compatible index.html that loads the React application from src/main.tsx"),
        ("src/App.tsx", "Generate a React App component that imports and demonstrates Login, Dashboard, Patients, and Doctors components"),
        ("src/main.tsx", "Generate a valid React entry point for Vite that mounts App into the document root"),
        ("src/Login.tsx", "Create a React login page with email, password and login button"),
        ("src/Dashboard.tsx", "Create a dashboard page with responsive statistic cards"),
        ("src/SectionOne.tsx", "Create a modern section component with a list or table for the first domain area"),
        ("src/SectionTwo.tsx", "Create a modern section component with a list or table for the second domain area"),
    ]

    generated_files: list[GeneratedFile] = []

    for filename, requirements in generation_tasks:
        if filename == "package.json":
            generated_code = frontend_generator.generate_package_json(project_name, requirements)
        elif filename == "index.html":
            generated_code = frontend_generator.generate_index_html(project_name, requirements)
        elif filename == "src/main.tsx":
            generated_code = frontend_generator.generate_main_tsx()
        else:
            # Generate each TSX component file separately
            generated_code = frontend_generator.generate_tsx(project_name, requirements, filename=filename)

        generated_files.append(GeneratedFile(path=f"generated_projects/hospital_management/frontend/{filename}", content=generated_code))

    generated_files.append(GeneratedFile(
        path="generated_projects/hospital_management/frontend/src/styles.css",
        content=frontend_generator.generate_styles_css(project_name, 'Generate shared application CSS for the React frontend'),
    ))

    # Generate deterministic frontend config files used by the Vite/TypeScript build.
    generated_files.extend([
        GeneratedFile(
            path="generated_projects/hospital_management/frontend/tsconfig.json",
            content=frontend_generator.generate_tsconfig_json(),
        ),
        GeneratedFile(
            path="generated_projects/hospital_management/frontend/tsconfig.app.json",
            content=frontend_generator.generate_tsconfig_app_json(),
        ),
        GeneratedFile(
            path="generated_projects/hospital_management/frontend/tsconfig.node.json",
            content=frontend_generator.generate_tsconfig_node_json(),
        ),
        GeneratedFile(
            path="generated_projects/hospital_management/frontend/vite.config.ts",
            content=frontend_generator.generate_vite_config_ts(),
        ),
    ])

    created_paths = file_writer.write_files(generated_files)

    for created_path in created_paths:
        print(f"GENERATED: {created_path.name}")
    print("AI CODE GENERATED")
    print("FILE CREATED")
    for created_path in created_paths:
        print(created_path)


def run_backend_generation_test() -> None:
    prompt = "Build a task management application using React FastAPI PostgreSQL with login and tasks."
    file_writer = FileWriter(Path(__file__).resolve().parents[3])
    backend_generator = BackendGenerator()
    frontend_generator = FrontendGenerator()

    generated_files = backend_generator.generate_files(type("Prompt", (), {"get_prompt": lambda self: prompt})())

    print("BACKEND AI CODE GENERATED")
    for generated_file in generated_files:
        print(generated_file.path)

    created_paths = file_writer.write_files(generated_files)
    print("BACKEND FILES CREATED")
    for created_path in created_paths:
        print(created_path)

    project_slug = backend_generator._project_slug(prompt)
    expected_paths = [
        file_writer.base_path / f"generated_projects/{project_slug}/backend/main.py",
        file_writer.base_path / f"generated_projects/{project_slug}/backend/database/connection.py",
        file_writer.base_path / f"generated_projects/{project_slug}/backend/database/session.py",
        file_writer.base_path / f"generated_projects/{project_slug}/backend/models/models.py",
        file_writer.base_path / f"generated_projects/{project_slug}/backend/schemas/schemas.py",
        file_writer.base_path / f"generated_projects/{project_slug}/backend/routers/routes.py",
    ]

    missing = [str(path) for path in expected_paths if not path.exists()]
    if missing:
        raise SystemExit(f"Expected backend files missing: {missing}")

    # Validate generated Python syntax for backend files
    for path in created_paths:
        if path.suffix == ".py":
            source = path.read_text(encoding="utf-8")
            try:
                __import__("ast").parse(source)
            except SyntaxError as exc:
                raise SystemExit(f"Generated Python file {path} contains syntax error: {exc}")

    # Validate generated JSON output for package.json via frontend generator
    package_json = frontend_generator.generate_package_json("Task Management", prompt)
    try:
        __import__("json").loads(package_json)
    except ValueError as exc:
        raise SystemExit(f"Generated package.json is invalid JSON: {exc}")

    print("BACKEND FILES VERIFIED")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "backend":
        run_backend_generation_test()
    else:
        main()
