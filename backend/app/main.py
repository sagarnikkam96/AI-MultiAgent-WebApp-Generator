"""FastAPI application entrypoint for the backend service."""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from .agents.orchestrator import MultiAgentOrchestrator
from .project_export.zip_generator import ZipGenerator


class AnalyzeRequest(BaseModel):
    """Request payload for requirement analysis."""

    user_prompt: str = Field(..., description="User prompt describing the project requirements")


# Directory that holds all generated projects (backend/generated_projects/<slug>/).
PROJECTS_ROOT = Path(__file__).resolve().parent.parent / "generated_projects"
EXPORTS_ROOT = Path(__file__).resolve().parent.parent / "exports"

app = FastAPI(
    title="AI Multi-Agent Web Application Generator Backend",
    version="0.1.0",
    description="Minimal FastAPI application for backend verification.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = MultiAgentOrchestrator()


def _resolve_project_dir(project_slug: str) -> Path:
    """Resolve a generated project directory safely (path traversal protection)."""
    if not project_slug:
        raise HTTPException(status_code=400, detail="Project slug is required")

    if "/" in project_slug or "\\" in project_slug or project_slug in (".", ".."):
        raise HTTPException(status_code=400, detail="Invalid project slug")

    project_dir = (PROJECTS_ROOT / project_slug).resolve()
    if PROJECTS_ROOT.resolve() not in project_dir.parents:
        raise HTTPException(status_code=400, detail="Invalid project slug")

    if not project_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Project '{project_slug}' not found")

    return project_dir


def _count_files(directory: Path) -> int:
    """Count all files (recursively) inside a directory."""
    if not directory.is_dir():
        return 0
    return sum(len(files) for _, _, files in os.walk(directory))


def _rewrite_index_assets(source_html: str, preview_prefix: str) -> str:
    """Rewrite built index.html asset references so they resolve under the
    preview mount point. Handles both absolute (/assets/...) and relative
    (./assets/...) paths produced by Vite builds (base '/' or base './')."""
    return re.sub(
        r'(["\'])\.?/assets/',
        rf"\g<1>{preview_prefix}/assets/",
        source_html,
    )


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    """Return the backend health response for startup verification."""
    return {
        "message": "AI Multi-Agent Web Application Generator Backend Running",
        "status": "success",
        "version": "0.1.0",
    }


@app.get("/health", tags=["health"])
def read_health() -> dict[str, str]:
    """Return backend health status (used by the frontend through the Vite proxy)."""
    return {
        "message": "AI Multi-Agent Web Application Generator Backend Running",
        "status": "success",
        "version": "0.1.0",
    }


@app.post("/analyze", tags=["requirements"])
def analyze_requirements(request: AnalyzeRequest) -> dict[str, Any]:
    """Analyze a user prompt and return the full orchestrator result."""
    return orchestrator.run(request.user_prompt)


@app.get("/projects/{project_slug}", tags=["projects"])
def get_project_status(project_slug: str) -> dict[str, Any]:
    """Return the status of a previously generated project."""
    project_dir = _resolve_project_dir(project_slug)
    frontend_dir = project_dir / "frontend"
    backend_dir = project_dir / "backend"
    dist_dir = frontend_dir / "dist"

    return {
        "slug": project_slug,
        "exists": True,
        "frontend": frontend_dir.is_dir(),
        "backend": backend_dir.is_dir(),
        "dist": dist_dir.is_dir(),
        "built": (dist_dir / "index.html").is_file(),
        "file_count": _count_files(project_dir),
        "frontend_file_count": _count_files(frontend_dir),
        "backend_file_count": _count_files(backend_dir),
    }


@app.get("/projects/{project_slug}/download", tags=["projects"])
def download_project(project_slug: str) -> FileResponse:
    """Return the generated project as a downloadable ZIP archive."""
    project_dir = _resolve_project_dir(project_slug)

    EXPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    archive_path = ZipGenerator(output_directory=EXPORTS_ROOT).generate_zip(
        project_dir,
        output_filename=project_slug,
    )

    return FileResponse(
        archive_path,
        media_type="application/zip",
        filename=f"{project_slug}.zip",
    )


@app.post("/projects/{project_slug}/build", tags=["projects"])
def build_project(project_slug: str) -> dict[str, Any]:
    """Install dependencies and build the generated React frontend for previewing."""
    project_dir = _resolve_project_dir(project_slug)
    frontend_dir = project_dir / "frontend"

    if not frontend_dir.is_dir():
        raise HTTPException(status_code=400, detail="Frontend directory is missing")
    if not (frontend_dir / "package.json").is_file():
        raise HTTPException(status_code=400, detail="package.json is missing in the frontend")

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise HTTPException(status_code=500, detail="Node/npm is not installed on this machine")

    def _run(command: list[str], timeout: int) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                [npm, *command],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(
                status_code=500,
                detail=f"Command timed out: {' '.join(command)}",
            ) from None

    install_result = _run(["install"], timeout=900)
    build_result = _run(["run", "build"], timeout=900)

    built = (frontend_dir / "dist" / "index.html").is_file()

    return {
        "slug": project_slug,
        "install_success": install_result.returncode == 0,
        "build_success": build_result.returncode == 0,
        "built": built,
        "install_log": "\n".join(
            [install_result.stdout[-2000:], install_result.stderr[-2000:]]
        ).strip(),
        "build_log": "\n".join(
            [build_result.stdout[-2000:], build_result.stderr[-2000:]]
        ).strip(),
    }


@app.get("/projects/{project_slug}/preview", tags=["projects"])
@app.get("/projects/{project_slug}/preview/{file_path:path}", tags=["projects"])
def preview_project(project_slug: str, file_path: str = "") -> FileResponse:
    """Serve the built generated website (SPA with index.html fallback)."""
    project_dir = _resolve_project_dir(project_slug)
    dist_dir = project_dir / "frontend" / "dist"

    if not (dist_dir / "index.html").is_file():
        raise HTTPException(
            status_code=404,
            detail="Website is not built yet. Click 'Build & Preview' first to create the runnable site.",
        )

    if not file_path:
        file_path = "index.html"

    target = (dist_dir / file_path).resolve()
    if dist_dir.resolve() != target and dist_dir.resolve() not in target.parents:
        raise HTTPException(status_code=400, detail="Invalid preview path")

    if target.is_file():
        # Rewrite absolute asset references (e.g. "/assets/...") produced by
        # builds that used the default Vite base so they resolve relative to
        # this preview mount point.
        if target.name == "index.html" and target.suffix == ".html":
            preview_prefix = f"/projects/{project_slug}/preview"
            source_html = target.read_text(encoding="utf-8")
            source_html = _rewrite_index_assets(source_html, preview_prefix)
            return HTMLResponse(content=source_html, media_type="text/html")

        return FileResponse(target)

    # SPA fallback: route client-side navigation paths back to index.html.
    index_file = dist_dir / "index.html"
    preview_prefix = f"/projects/{project_slug}/preview"
    source_html = index_file.read_text(encoding="utf-8")
    source_html = _rewrite_index_assets(source_html, preview_prefix)
    return HTMLResponse(content=source_html, media_type="text/html")

