"""Testing Agent for validating generated full-stack web applications."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from typing import Any

from .base_agent import BaseAgent
from .schemas import TestingReport, TestingCheck


class TestingAgent(BaseAgent):
    """Agent that performs real structural, syntax, schema, and configuration tests on generated code."""

    def __init__(self, name: str = "testing_agent") -> None:
        super().__init__(name=name, description="Performs automated validation and testing of generated full-stack code")

    def analyze(self, user_prompt: str) -> Any:
        return user_prompt

    def test_project(self, project_dir: Path | str) -> TestingReport:
        """Run complete automated validation suite on a generated project directory."""
        dir_path = Path(project_dir).resolve()
        if not dir_path.is_dir():
            return TestingReport(
                is_valid=False,
                passed_count=0,
                failed_count=1,
                checks=[
                    TestingCheck(
                        name="project_directory_exists",
                        category="structure",
                        passed=False,
                        details=f"Project directory '{dir_path}' does not exist on disk.",
                    )
                ],
                errors=[f"Project directory not found: {dir_path}"],
                logs=f"Failed to locate project directory at {dir_path}",
            )

        checks: list[TestingCheck] = []
        errors: list[str] = []
        logs_list: list[str] = []

        # 1. Project Structure Validation
        structure_checks, structure_errors = self._validate_structure(dir_path)
        checks.extend(structure_checks)
        errors.extend(structure_errors)

        # 2. Backend Python Syntax & AST Validation
        backend_dir = dir_path / "backend"
        if backend_dir.is_dir():
            py_checks, py_errors = self._validate_python_files(backend_dir)
            checks.extend(py_checks)
            errors.extend(py_errors)

            # 3. Database Models & Schema Validation
            db_checks, db_errors = self._validate_database_models(backend_dir)
            checks.extend(db_checks)
            errors.extend(db_errors)

            # 4. FastAPI Routes & Security Imports
            route_checks, route_errors = self._validate_fastapi_routes(backend_dir)
            checks.extend(route_checks)
            errors.extend(route_errors)

        # 5. Frontend Files & Configurations Validation
        frontend_dir = dir_path / "frontend"
        if frontend_dir.is_dir():
            fe_checks, fe_errors = self._validate_frontend_config(frontend_dir)
            checks.extend(fe_checks)
            errors.extend(fe_errors)

        passed_count = sum(1 for c in checks if c.passed)
        failed_count = sum(1 for c in checks if not c.passed)
        is_valid = failed_count == 0

        logs = "\n".join([
            f"=== Generated Project Validation Report ===",
            f"Directory: {dir_path}",
            f"Total Checks: {len(checks)} | Passed: {passed_count} | Failed: {failed_count}",
            "",
            *[f"[{'PASS' if c.passed else 'FAIL'}] ({c.category.upper()}) {c.name}: {c.details}" for c in checks],
            "",
            *(["--- Errors Detected ---", *errors] if errors else ["All checks passed successfully!"]),
        ])

        return TestingReport(
            is_valid=is_valid,
            passed_count=passed_count,
            failed_count=failed_count,
            checks=checks,
            errors=errors,
            logs=logs,
        )

    def _validate_structure(self, project_dir: Path) -> tuple[list[TestingCheck], list[str]]:
        checks: list[TestingCheck] = []
        errors: list[str] = []

        frontend_dir = project_dir / "frontend"
        backend_dir = project_dir / "backend"

        if frontend_dir.is_dir():
            checks.append(TestingCheck(name="frontend_directory", category="structure", passed=True, details="frontend/ directory exists"))
        else:
            checks.append(TestingCheck(name="frontend_directory", category="structure", passed=False, details="Missing frontend/ directory"))
            errors.append("Missing frontend/ directory")

        if backend_dir.is_dir():
            checks.append(TestingCheck(name="backend_directory", category="structure", passed=True, details="backend/ directory exists"))
        else:
            checks.append(TestingCheck(name="backend_directory", category="structure", passed=False, details="Missing backend/ directory"))
            errors.append("Missing backend/ directory")

        return checks, errors

    def _validate_python_files(self, backend_dir: Path) -> tuple[list[TestingCheck], list[str]]:
        checks: list[TestingCheck] = []
        errors: list[str] = []

        python_files = list(backend_dir.rglob("*.py"))
        if not python_files:
            checks.append(TestingCheck(name="python_files_exist", category="backend", passed=False, details="No Python files found in backend/"))
            errors.append("No Python files found in backend/")
            return checks, errors

        checks.append(TestingCheck(name="python_files_exist", category="backend", passed=True, details=f"Found {len(python_files)} Python source files"))

        for py_file in python_files:
            rel_path = str(py_file.relative_to(backend_dir))
            try:
                source_code = py_file.read_text(encoding="utf-8")
                ast.parse(source_code, filename=str(py_file))
                checks.append(TestingCheck(
                    name=f"syntax_{rel_path}",
                    category="backend",
                    passed=True,
                    details=f"Valid Python AST syntax: {rel_path}",
                ))
            except SyntaxError as exc:
                err_msg = f"Syntax error in {rel_path} (line {exc.lineno}): {exc.msg}"
                checks.append(TestingCheck(
                    name=f"syntax_{rel_path}",
                    category="backend",
                    passed=False,
                    details=err_msg,
                ))
                errors.append(err_msg)
            except Exception as exc:
                err_msg = f"Failed to read/parse {rel_path}: {exc}"
                checks.append(TestingCheck(
                    name=f"parse_{rel_path}",
                    category="backend",
                    passed=False,
                    details=err_msg,
                ))
                errors.append(err_msg)

        return checks, errors

    def _validate_database_models(self, backend_dir: Path) -> tuple[list[TestingCheck], list[str]]:
        checks: list[TestingCheck] = []
        errors: list[str] = []

        app_dir = backend_dir / "app" if (backend_dir / "app").is_dir() else backend_dir
        models_file = app_dir / "models" / "models.py"
        if not models_file.is_file():
            # Check if models exist directly
            return checks, errors

        try:
            content = models_file.read_text(encoding="utf-8")
            parsed = ast.parse(content, filename="models.py")

            classes = [node.name for node in ast.walk(parsed) if isinstance(node, ast.ClassDef)]
            if classes:
                checks.append(TestingCheck(
                    name="database_models_declared",
                    category="database",
                    passed=True,
                    details=f"Declared models: {', '.join(classes)}",
                ))
            else:
                checks.append(TestingCheck(
                    name="database_models_declared",
                    category="database",
                    passed=False,
                    details="No model classes found in models/models.py",
                ))
                errors.append("No model classes found in models/models.py")
        except Exception as exc:
            err_msg = f"Error inspecting database models: {exc}"
            checks.append(TestingCheck(name="database_models_valid", category="database", passed=False, details=err_msg))
            errors.append(err_msg)

        return checks, errors

    def _validate_fastapi_routes(self, backend_dir: Path) -> tuple[list[TestingCheck], list[str]]:
        checks: list[TestingCheck] = []
        errors: list[str] = []

        app_dir = backend_dir / "app" if (backend_dir / "app").is_dir() else backend_dir
        main_file = app_dir / "main.py"
        routes_file = app_dir / "routers" / "routes.py"

        if main_file.is_file():
            content = main_file.read_text(encoding="utf-8")
            has_fastapi = "FastAPI(" in content
            checks.append(TestingCheck(
                name="fastapi_app_instantiation",
                category="backend",
                passed=has_fastapi,
                details="FastAPI() app initialized in main.py" if has_fastapi else "FastAPI() instance missing in main.py",
            ))
            if not has_fastapi:
                errors.append("FastAPI() instance missing in main.py")

        if routes_file.is_file():
            content = routes_file.read_text(encoding="utf-8")
            # Check for missing imports like OAuth2PasswordBearer
            if "OAuth2PasswordBearer(" in content and "from fastapi.security import" not in content:
                err_msg = "OAuth2PasswordBearer used in routes.py but missing security import"
                checks.append(TestingCheck(name="security_import_check", category="backend", passed=False, details=err_msg))
                errors.append(err_msg)
            else:
                checks.append(TestingCheck(name="security_import_check", category="backend", passed=True, details="Security imports resolved in routes.py"))

        return checks, errors

    def _validate_frontend_config(self, frontend_dir: Path) -> tuple[list[TestingCheck], list[str]]:
        checks: list[TestingCheck] = []
        errors: list[str] = []

        package_json = frontend_dir / "package.json"
        if package_json.is_file():
            try:
                pkg = json.loads(package_json.read_text(encoding="utf-8"))
                has_react = "react" in pkg.get("dependencies", {})
                checks.append(TestingCheck(
                    name="frontend_package_json",
                    category="frontend",
                    passed=has_react,
                    details=f"Valid package.json with React ({pkg.get('name', 'frontend')})",
                ))
            except Exception as exc:
                err_msg = f"Invalid package.json in frontend: {exc}"
                checks.append(TestingCheck(name="frontend_package_json", category="frontend", passed=False, details=err_msg))
                errors.append(err_msg)
        else:
            checks.append(TestingCheck(name="frontend_package_json", category="frontend", passed=False, details="Missing package.json in frontend/"))
            errors.append("Missing package.json in frontend/")

        main_tsx = frontend_dir / "src" / "main.tsx"
        app_tsx = frontend_dir / "src" / "App.tsx"

        if main_tsx.is_file():
            checks.append(TestingCheck(name="frontend_entry_point", category="frontend", passed=True, details="src/main.tsx exists"))
        else:
            checks.append(TestingCheck(name="frontend_entry_point", category="frontend", passed=False, details="src/main.tsx missing"))
            errors.append("src/main.tsx missing")

        if app_tsx.is_file():
            checks.append(TestingCheck(name="frontend_app_component", category="frontend", passed=True, details="src/App.tsx exists"))
        else:
            checks.append(TestingCheck(name="frontend_app_component", category="frontend", passed=False, details="src/App.tsx missing"))
            errors.append("src/App.tsx missing")

        return checks, errors
