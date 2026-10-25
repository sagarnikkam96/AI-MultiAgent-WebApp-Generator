"""Debugging Agent for automated error diagnosis and code self-healing."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

from .base_agent import BaseAgent
from .schemas import DebugReport, DebugFix, TestingReport
from .testing_agent import TestingAgent


class DebuggingAgent(BaseAgent):
    """Agent that diagnoses errors discovered by the Testing Agent and applies automated code repairs."""

    def __init__(self, name: str = "debugging_agent", max_attempts: int = 3) -> None:
        super().__init__(name=name, description="Analyzes testing failures and applies targeted code repairs in a feedback loop")
        self.max_attempts = max_attempts
        self.testing_agent = TestingAgent()

    def analyze(self, user_prompt: str) -> Any:
        return user_prompt

    def debug_loop(self, project_dir: Path | str, initial_report: TestingReport | None = None) -> tuple[TestingReport, DebugReport]:
        """Run iterative debug and repair loop until tests pass or attempts are exhausted."""
        dir_path = Path(project_dir).resolve()
        current_report = initial_report or self.testing_agent.test_project(dir_path)

        if current_report.is_valid:
            return current_report, DebugReport(
                attempts=0,
                succeeded=True,
                fixes=[],
                message="Project passed all testing checks on initial run. No debugging required.",
                remaining_blockers=[],
            )

        applied_fixes: list[DebugFix] = []
        attempt = 0

        while attempt < self.max_attempts and not current_report.is_valid:
            attempt += 1
            iteration_fixes = self._diagnose_and_repair(dir_path, current_report)
            applied_fixes.extend(iteration_fixes)

            # Re-test after repairs
            current_report = self.testing_agent.test_project(dir_path)

        succeeded = current_report.is_valid
        remaining = current_report.errors if not succeeded else []

        message = (
            f"Debugging loop succeeded after {attempt} attempt(s) with {len(applied_fixes)} fix(es) applied."
            if succeeded else
            f"Debugging completed with {len(remaining)} blocker(s) remaining after {attempt} attempt(s)."
        )

        debug_report = DebugReport(
            attempts=attempt,
            succeeded=succeeded,
            fixes=applied_fixes,
            message=message,
            remaining_blockers=remaining,
        )

        return current_report, debug_report

    def _diagnose_and_repair(self, project_dir: Path, report: TestingReport) -> list[DebugFix]:
        fixes: list[DebugFix] = []

        for error in report.errors:
            # 1. Missing OAuth2PasswordBearer security import
            if "OAuth2PasswordBearer" in error:
                fix = self._fix_oauth2_import(project_dir)
                if fix:
                    fixes.append(fix)

            # 2. Syntax error in python files (e.g. markdown code fence or stray token)
            elif "Syntax error in" in error:
                match = re.search(r"Syntax error in ([^\s:]+)", error)
                if match:
                    rel_file = match.group(1)
                    backend_dir = project_dir / "backend"
                    nested_path = backend_dir / "app" / rel_file
                    target_path = nested_path if nested_path.is_file() else backend_dir / rel_file
                    fix = self._fix_python_syntax(target_path, rel_file)
                    if fix:
                        fixes.append(fix)

            # 3. Invalid package.json in frontend
            elif "package.json" in error.lower():
                fix = self._fix_package_json(project_dir / "frontend" / "package.json")
                if fix:
                    fixes.append(fix)

            # 4. Missing main.tsx entry point
            elif "main.tsx missing" in error:
                fix = self._fix_main_tsx(project_dir / "frontend" / "src" / "main.tsx")
                if fix:
                    fixes.append(fix)

        return fixes

    def _fix_oauth2_import(self, project_dir: Path) -> DebugFix | None:
        backend_dir = project_dir / "backend"
        nested_routes_file = backend_dir / "app" / "routers" / "routes.py"
        routes_file = nested_routes_file if nested_routes_file.is_file() else backend_dir / "routers" / "routes.py"
        if not routes_file.is_file():
            return None

        content = routes_file.read_text(encoding="utf-8")
        if "from fastapi.security import OAuth2PasswordBearer" not in content and "OAuth2PasswordBearer(" in content:
            new_content = "from fastapi.security import OAuth2PasswordBearer\n" + content
            routes_file.write_text(new_content, encoding="utf-8")
            return DebugFix(
                file_path="backend/routers/routes.py",
                issue_type="import",
                root_cause="OAuth2PasswordBearer referenced without import from fastapi.security",
                fix_description="Prepended 'from fastapi.security import OAuth2PasswordBearer' import.",
                applied=True,
            )
        return None

    def _fix_python_syntax(self, py_path: Path, rel_name: str) -> DebugFix | None:
        if not py_path.is_file():
            return None

        content = py_path.read_text(encoding="utf-8")
        # Remove markdown codeblocks or triple backticks
        cleaned = re.sub(r"^```(?:python)?\n?", "", content, flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.replace("```", "")

        try:
            ast.parse(cleaned)
            py_path.write_text(cleaned.strip() + "\n", encoding="utf-8")
            return DebugFix(
                file_path=f"backend/{rel_name}",
                issue_type="syntax",
                root_cause="Stray markdown artifacts or invalid code fence inside Python file",
                fix_description="Stripped markdown fences and reformatted Python code to valid AST.",
                applied=True,
            )
        except Exception:
            return None

    def _fix_package_json(self, pkg_path: Path) -> DebugFix | None:
        if not pkg_path.is_file():
            return None
        content = pkg_path.read_text(encoding="utf-8")
        cleaned = re.sub(r"^```(?:json)?\n?", "", content, flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.replace("```", "")
        try:
            parsed = json.loads(cleaned)
            formatted = json.dumps(parsed, indent=2)
            pkg_path.write_text(formatted, encoding="utf-8")
            return DebugFix(
                file_path="frontend/package.json",
                issue_type="config",
                root_cause="Malformed package.json syntax",
                fix_description="Reformatted package.json with standard JSON parser.",
                applied=True,
            )
        except Exception:
            return None

    def _fix_main_tsx(self, main_path: Path) -> DebugFix | None:
        main_path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            "import React from 'react';\n"
            "import ReactDOM from 'react-dom/client';\n"
            "import App from './App';\n"
            "import './styles.css';\n\n"
            "const rootElement = document.getElementById('root');\n"
            "if (rootElement) {\n"
            "  ReactDOM.createRoot(rootElement).render(\n"
            "    <React.StrictMode>\n"
            "      <App />\n"
            "    </React.StrictMode>\n"
            "  );\n"
            "}\n"
        )
        main_path.write_text(content, encoding="utf-8")
        return DebugFix(
            file_path="frontend/src/main.tsx",
            issue_type="missing_file",
            root_cause="Missing React entrypoint file main.tsx",
            fix_description="Created standard React 18 createRoot entrypoint in src/main.tsx.",
            applied=True,
        )
