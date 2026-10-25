from __future__ import annotations

import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from app import main


class ProjectBuildProgressTests(unittest.TestCase):
    def test_build_runs_in_background_and_reuses_installed_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            projects_root = Path(temporary_dir)
            frontend_dir = projects_root / "sample" / "frontend"
            frontend_dir.mkdir(parents=True)
            (frontend_dir / "package.json").write_text('{"scripts":{"build":"vite build"}}', encoding="utf-8")
            calls: list[list[str]] = []

            def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                calls.append(command)
                if "install" in command:
                    (frontend_dir / "node_modules").mkdir(exist_ok=True)
                else:
                    dist_dir = frontend_dir / "dist"
                    dist_dir.mkdir(exist_ok=True)
                    (dist_dir / "index.html").write_text("<html></html>", encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, "ok", "")

            with (
                patch.object(main, "PROJECTS_ROOT", projects_root),
                patch.object(main.shutil, "which", return_value="npm.cmd"),
                patch.object(main.subprocess, "run", side_effect=fake_run),
            ):
                first_job = main.build_project("sample")
                completed = self._wait_for_completion("sample")
                self.assertIn(first_job["status"], {"queued", "installing", "building", "completed"})
                self.assertEqual(completed["status"], "completed")
                self.assertTrue(completed["build_success"])
                self.assertEqual([command[1] for command in calls], ["install", "run"])

                calls.clear()
                main.build_project("sample")
                second_build = self._wait_for_completion("sample")
                self.assertEqual(second_build["status"], "completed")
                self.assertEqual([command[1] for command in calls], ["run"])

            with main._BUILD_JOBS_LOCK:
                main._BUILD_JOBS.pop("sample", None)

    def _wait_for_completion(self, project_slug: str) -> dict[str, object]:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            status = main.get_project_build_status(project_slug)
            if status["status"] in {"completed", "failed"}:
                return status
            time.sleep(0.01)
        self.fail("Frontend build did not finish before the test deadline")


if __name__ == "__main__":
    unittest.main()
