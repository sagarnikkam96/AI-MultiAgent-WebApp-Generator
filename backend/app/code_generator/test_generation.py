from __future__ import annotations

import sys
from pathlib import Path

# Ensure the local `app` package is importable when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
        ("src/Dashboard.tsx", "Create a hospital dashboard page showing summary cards"),
        ("src/Patients.tsx", "Create a patient management page with a patient list"),
        ("src/Doctors.tsx", "Create a doctor management page with a doctor list"),
    ]

    generated_files: list[GeneratedFile] = []

    for filename, requirements in generation_tasks:
        if filename == "package.json":
            generated_code = frontend_generator.generate_package_json(project_name, requirements)
        elif filename == "index.html":
            generated_code = frontend_generator.generate_index_html(project_name, requirements)
        else:
            # Generate each TSX/entry file separately
            generated_code = frontend_generator.generate_tsx(project_name, requirements)

        generated_files.append(GeneratedFile(path=f"generated_projects/hospital_management/frontend/{filename}", content=generated_code))

    created_paths = file_writer.write_files(generated_files)

    for created_path in created_paths:
        print(f"GENERATED: {created_path.name}")
    print("AI CODE GENERATED")
    print("FILE CREATED")
    for created_path in created_paths:
        print(created_path)


if __name__ == "__main__":
    main()
