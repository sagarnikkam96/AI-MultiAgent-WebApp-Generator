"""FastAPI application entrypoint for the backend service."""

import os
import re
import shutil
import subprocess
import hashlib
import json
import secrets
import tempfile
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Any, Literal

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, Response
from pydantic import BaseModel, Field, field_validator
from .database.auth_db import get_db_connection, get_generated_projects, record_generated_project

from .agents.orchestrator import MultiAgentOrchestrator
from .agents.backend_schema import BackendBlueprint
from .agents.database_schema import DatabaseBlueprint
from .agents.planner_schema import ProjectPlan
from .agents.schemas import RequirementSchema
from .api import auth
from .api.auth import get_current_user, get_optional_current_user
from .language_catalog import LANGUAGE_NAMES
from .multimodal.extractor import extract_attachment
from .project_export.zip_generator import ZipGenerator
from .visual_design import PremiumDesignEngine


class AnalyzeRequest(BaseModel):
    """Request payload for requirement analysis."""

    user_prompt: str = Field(..., description="User prompt describing the project requirements")
    language: str = Field(
        default="en",
        description=f"Requested output language code. Supported codes: {', '.join(LANGUAGE_NAMES)}",
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if value not in LANGUAGE_NAMES:
            raise ValueError(f"Unsupported output language code: {value}")
        return value


class SDLCGenerationRequest(AnalyzeRequest):
    """Approved requirements and design used to generate an SDLC project."""

    approved: bool = Field(default=False, description="Whether the submitted design was explicitly approved")
    requirements: RequirementSchema
    project_plan: ProjectPlan
    backend_blueprint: BackendBlueprint
    database_blueprint: DatabaseBlueprint


class PremiumDesignRequest(BaseModel):
    """Art-direction request for a CSS-only generated-site enhancement."""

    user_prompt: str = Field(default="", max_length=3000)
    style: Literal[
        "auto",
        "futuristic",
        "luxury",
        "cinematic",
        "creative",
        "editorial",
        "organic",
        "minimalist",
        "glassmorphism",
        "bold",
    ] = "auto"


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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.post("/login", tags=["auth"])
def legacy_login(req: auth.LoginRequest) -> dict[str, Any]:
    """Backward-compatible route for older clients that still hit /login."""
    return auth.login(req)


@app.post("/register", tags=["auth"])
def legacy_register(req: auth.RegisterRequest) -> dict[str, Any]:
    """Backward-compatible route for older clients that still hit /register."""
    return auth.register(req)


@app.post("/api/login", tags=["auth"])
def legacy_api_login(req: auth.LoginRequest) -> dict[str, Any]:
    """Compatibility route for older APIs using /api/login."""
    return auth.login(req)


@app.post("/api/register", tags=["auth"])
def legacy_api_register(req: auth.RegisterRequest) -> dict[str, Any]:
    """Compatibility route for older APIs using /api/register."""
    return auth.register(req)


orchestrator = MultiAgentOrchestrator()
premium_design_engine = PremiumDesignEngine(model_client=orchestrator.ollama_client)
PREMIUM_DESIGN_ROOT = EXPORTS_ROOT / ".premium-design-previews"
_BUILD_JOBS: dict[str, dict[str, Any]] = {}
_BUILD_JOBS_LOCK = threading.Lock()
_BUILD_COMMAND_TIMEOUT_SECONDS = 300


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


@app.get("/api/dashboard/counts", tags=["dashboard"])
def get_dashboard_counts() -> dict[str, int]:
    """Return dynamic counts for dashboard metrics from the database.

    Currently calculates total patients from the auth users table.
    Extend this function to include other domain‑specific tables as needed.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_patients = cursor.fetchone()[0]
    # Placeholder values for other metrics; replace with real queries when tables exist.
    appointments_today = 0
    available_beds = 0
    return {
        "total_patients": total_patients,
        "appointments_today": appointments_today,
        "available_beds": available_beds,
    }


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


class GenerateImageRequest(BaseModel):
    """Request payload for image generation."""

    prompt: str = Field(..., description="Text prompt describing the image to generate")
    width: int = Field(default=512, description="Image width in pixels")
    height: int = Field(default=512, description="Image height in pixels")
    seed: int | None = Field(default=None, description="Random seed for reproducibility")


@app.post("/api/generate-image", tags=["multimodal"])
def generate_image(request: GenerateImageRequest) -> dict[str, Any]:
    """Generate an image from a text prompt using Pollinations.ai (free, no key required).

    Returns a direct image URL that the frontend can display or download.
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    encoded_prompt = urllib.parse.quote(request.prompt.strip())
    seed = request.seed if request.seed is not None else __import__('random').randint(1, 999999)
    image_url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={request.width}&height={request.height}&nologo=true&seed={seed}"
    )

    return {
        "prompt": request.prompt,
        "width": request.width,
        "height": request.height,
        "seed": seed,
        "image_url": image_url,
    }


class GenerateVideoRequest(BaseModel):
    """Request payload for video generation."""

    prompt: str = Field(..., description="Text prompt describing the video to generate")
    width: int = Field(default=1280, description="Video width in pixels")
    height: int = Field(default=720, description="Video height in pixels")
    theme: str = Field(default="cyberpunk", description="Visual theme style (cyberpunk, modern_saas, neon_abstract, wireframe)")
    seed: int | None = Field(default=None, description="Random seed for reproducibility")


class ExplainProjectRequest(BaseModel):
    """Request payload to explain the project with voice narration."""

    prompt: str = Field(..., description="Project prompt or name")
    project_slug: str | None = Field(default=None, description="Optional project slug")
    language: str = Field(default="en", description="Output language")


@app.post("/api/generate-video", tags=["multimodal"])
def generate_video(request: GenerateVideoRequest) -> dict[str, Any]:
    """Generate a procedural AI motion video with storyboard scenes, scripts, and video metadata."""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    encoded_prompt = urllib.parse.quote(request.prompt.strip())
    seed = request.seed if request.seed is not None else __import__('random').randint(1, 999999)
    clean_prompt = request.prompt.strip()

    # Generate procedural storyboard scenes based on prompt domain
    scenes = [
        {
            "id": 1,
            "title": f"🚀 Introducing {clean_prompt[:30].title()}",
            "subtitle": "AI Autonomous Multi-Agent Web Architecture",
            "type": "intro",
            "duration": 4.0,
            "color": "#6366f1",
            "accent": "#a855f7",
            "voiceover": f"Welcome to the next generation web application for {clean_prompt}."
        },
        {
            "id": 2,
            "title": "⚡ Multi-Agent Orchestration Flow",
            "subtitle": "Requirement Analysis • Architecture Planning • Code Generation",
            "type": "architecture",
            "duration": 4.5,
            "color": "#06b6d4",
            "accent": "#3b82f6",
            "voiceover": "Autonomous AI agents analyze domain requirements, design schema relationships, and assemble responsive components."
        },
        {
            "id": 3,
            "title": "🛠 Full-Stack React & FastAPI Engine",
            "subtitle": "Interactive UI • RESTful APIs • SQLite & PostgreSQL",
            "type": "tech_stack",
            "duration": 4.5,
            "color": "#10b981",
            "accent": "#059669",
            "voiceover": "Built with modern React 18, TypeScript, and high-performance FastAPI backends ready for production."
        },
        {
            "id": 4,
            "title": "✨ Live Interactive Deployment",
            "subtitle": "One-Click In-Browser Preview & VS Code Workspace",
            "type": "demo",
            "duration": 4.0,
            "color": "#f59e0b",
            "accent": "#ea580c",
            "voiceover": "Test the live interactive preview, iterate custom requirements, and download the full working workspace."
        }
    ]

    return {
        "prompt": request.prompt,
        "width": request.width,
        "height": request.height,
        "theme": request.theme,
        "seed": seed,
        "duration_seconds": sum(s["duration"] for s in scenes),
        "scenes": scenes,
        "audio_script": " ".join(s["voiceover"] for s in scenes),
        "video_url": f"https://image.pollinations.ai/prompt/{encoded_prompt}%20cinematic%20tech%20motion%20graphics?width={request.width}&height={request.height}&nologo=true&seed={seed}",
    }


@app.post("/api/explain-project", tags=["requirements"])
def explain_project(request: ExplainProjectRequest) -> dict[str, Any]:
    """Generate audio narration and explanation for a project."""
    prompt = request.prompt.strip() or "Web Application"
    analysis = orchestrator.requirement_agent.analyze(prompt)
    project_name = getattr(analysis, "project_name", "Generated Project") or "Web App"
    project_type = getattr(analysis, "project_type", "Web Application")
    modules = getattr(analysis, "modules", []) or ["Dashboard", "Data Records"]
    frontend = getattr(analysis, "frontend", "React")
    backend = getattr(analysis, "backend", "FastAPI")
    database = getattr(analysis, "database", "PostgreSQL")

    narration_script = orchestrator.hybrid_engine.generate_narration_script(
        project_name=project_name,
        project_type=project_type,
        modules=modules,
        frontend=frontend,
        backend=backend,
        database=database,
    )

    summary = orchestrator.hybrid_engine.generate_summary(
        project_name=project_name,
        project_type=project_type,
        modules=modules,
        frontend=frontend,
        backend=backend,
        database=database,
    )

    return {
        "project_name": project_name,
        "project_type": project_type,
        "modules": modules,
        "tech_stack": {
            "frontend": frontend,
            "backend": backend,
            "database": database,
        },
        "narration_script": narration_script,
        "summary": summary,
    }


@app.post("/analyze", tags=["requirements"])
def analyze_requirements(
    request: AnalyzeRequest,
    current_user: dict[str, Any] | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Analyze a user prompt and return the full orchestrator result."""
    result = orchestrator.run(request.user_prompt, language=request.language)
    _record_user_project(result, current_user)
    return result


@app.post("/api/sdlc/plan", tags=["sdlc"])
def plan_sdlc(request: AnalyzeRequest) -> dict[str, Any]:
    """Return an SRS and system design for review before any application is generated."""
    if not request.user_prompt.strip():
        raise HTTPException(status_code=400, detail="A problem statement is required")
    return orchestrator.plan_sdlc(request.user_prompt, language=request.language)


@app.post("/api/sdlc/generate", tags=["sdlc"])
def generate_approved_sdlc(
    request: SDLCGenerationRequest,
    current_user: dict[str, Any] | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Generate and validate an application only from an explicitly approved design."""
    if not request.approved:
        raise HTTPException(status_code=400, detail="Approve the requirements and system design before generation")
    result = orchestrator.run(
        request.user_prompt,
        language=request.language,
        requirements=request.requirements,
        project_plan=request.project_plan,
        backend_blueprint=request.backend_blueprint,
        database_blueprint=request.database_blueprint,
    )
    _record_user_project(result, current_user)
    return result


@app.post("/api/multimodal/analyze", tags=["requirements"])
async def analyze_multimodal(
    text: str = Form(""),
    files: list[UploadFile] = File(default=[]),
    language: str = Form(default="en"),
    current_user: dict[str, Any] | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Analyze a requirements prompt augmented by uploaded text/image/audio/video files.

    This is an additive, multimodal companion to ``/analyze``. It combines the
    typed/speech text with any text extracted from uploaded files and runs the
    exact same multi-agent pipeline, so the core text generation is untouched.
    Extraction is graceful: any file that can't be parsed is attached for
    reference with a descriptive note instead of failing the request.
    """
    if language not in LANGUAGE_NAMES:
        raise HTTPException(status_code=422, detail=f"Unsupported output language code: {language}")

    combined_text = text or ""
    attachments: list[dict[str, Any]] = []

    for upload in files:
        filename = upload.filename or "upload"
        if not filename.strip() or filename == "upload":
            continue

        data = await upload.read()
        extracted = extract_attachment(filename, data)
        attachments.append(
            {
                "filename": filename,
                "kind": extracted.kind,
                "extracted": extracted.extracted,
                "note": extracted.note,
            }
        )

        if extracted.extracted and extracted.extracted.strip():
            combined_text += f"\n\n--- Content extracted from {filename} ---\n{extracted.extracted}"
        else:
            combined_text += f"\n\n[Attachment: {filename} ({extracted.kind}) - {extracted.note}]"

    if not combined_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide some text (typed or spoken) and/or at least one file.",
        )

    result = orchestrator.run(combined_text, language=language)
    result["multimodal"] = {"attachments": attachments}
    _record_user_project(result, current_user)
    return result


def _record_user_project(result: dict[str, Any], current_user: dict[str, Any] | None) -> None:
    """Associate a successfully generated project with the authenticated user."""
    if not current_user:
        return
    project = result.get("generated_project") or {}
    project_slug = project.get("project_slug")
    if not project_slug or project.get("error"):
        return
    requirements = result.get("requirements") or {}
    project_name = project.get("project_name") or requirements.get("project_name") or project_slug
    record_generated_project(current_user["id"], project_slug, str(project_name))


@app.get("/api/projects/history", tags=["projects"])
def get_project_history(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    """List generated websites belonging to the currently signed-in user."""
    projects = []
    for project in get_generated_projects(current_user["id"]):
        project_dir = PROJECTS_ROOT / project["project_slug"]
        built = (project_dir / "frontend" / "dist" / "index.html").is_file()
        projects.append({**project, "built": built})
    return {"projects": projects, "count": len(projects)}



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


@app.get("/projects/{project_slug}/files/{file_path:path}", tags=["projects"])
def read_project_file(project_slug: str, file_path: str) -> PlainTextResponse:
    """Return a generated source file for the in-app code viewer."""
    project_dir = _resolve_project_dir(project_slug)
    requested_file = (project_dir / file_path).resolve()
    project_root = project_dir.resolve()
    if project_root not in requested_file.parents or not requested_file.is_file():
        raise HTTPException(status_code=404, detail="Generated file was not found")

    try:
        content = requested_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=415, detail="Generated file is not a text file") from exc

    return PlainTextResponse(content)


@app.post("/projects/{project_slug}/build", tags=["projects"])
def build_project(project_slug: str) -> dict[str, Any]:
    """Start a background frontend build so clients can poll progress."""
    project_dir = _resolve_project_dir(project_slug)
    frontend_dir = project_dir / "frontend"

    if not frontend_dir.is_dir():
        raise HTTPException(status_code=400, detail="Frontend directory is missing")
    if not (frontend_dir / "package.json").is_file():
        raise HTTPException(status_code=400, detail="package.json is missing in the frontend")

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise HTTPException(status_code=500, detail="Node/npm is not installed on this machine")

    with _BUILD_JOBS_LOCK:
        existing_job = _BUILD_JOBS.get(project_slug)
        if existing_job and existing_job["status"] in {"queued", "installing", "building"}:
            return dict(existing_job)
        _BUILD_JOBS[project_slug] = {
            "slug": project_slug,
            "status": "queued",
            "phase": "Preparing build...",
            "install_success": False,
            "build_success": False,
            "built": False,
            "install_log": "",
            "build_log": "",
        }

    def _update_job(**updates: Any) -> None:
        with _BUILD_JOBS_LOCK:
            _BUILD_JOBS[project_slug].update(updates)

    def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                [npm, *command],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=_BUILD_COMMAND_TIMEOUT_SECONDS,
                shell=False,
            )
        except subprocess.TimeoutExpired as error:
            output = error.stdout or ""
            if isinstance(output, bytes):
                output = output.decode(errors="replace")
            stderr = error.stderr or ""
            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors="replace")
            raise TimeoutError(
                f"npm {' '.join(command)} timed out after "
                f"{_BUILD_COMMAND_TIMEOUT_SECONDS} seconds.\n{output}\n{stderr}".strip()
            ) from error

    def _run_build() -> None:
        install_log = ""
        build_log = ""
        install_success = False
        try:
            package_json = frontend_dir / "package.json"
            lock_file = frontend_dir / "package-lock.json"
            dependency_stamp = frontend_dir / "node_modules" / ".generator-dependencies.sha256"

            def _dependency_key() -> str:
                return hashlib.sha256(
                    package_json.read_bytes() + (lock_file.read_bytes() if lock_file.is_file() else b"")
                ).hexdigest()

            dependency_key = _dependency_key()
            dependencies_ready = (
                dependency_stamp.is_file()
                and dependency_stamp.read_text(encoding="utf-8").strip() == dependency_key
                and (frontend_dir / "node_modules").is_dir()
            )

            install_success = dependencies_ready
            if not dependencies_ready:
                _update_job(status="installing", phase="Installing frontend dependencies...")
                install_result = _run([
                    "install",
                    "--no-audit",
                    "--no-fund",
                    "--prefer-offline",
                ])
                install_log = "\n".join(
                    [install_result.stdout[-4000:], install_result.stderr[-4000:]]
                ).strip()
                install_success = install_result.returncode == 0
                if not install_success:
                    _update_job(
                        status="failed",
                        phase="Dependency installation failed.",
                        install_success=False,
                        install_log=install_log,
                        built=(frontend_dir / "dist" / "index.html").is_file(),
                    )
                    return
                dependency_key = _dependency_key()
                dependency_stamp.parent.mkdir(parents=True, exist_ok=True)
                dependency_stamp.write_text(dependency_key, encoding="utf-8")

            _update_job(
                status="building",
                phase="Building frontend assets...",
                install_success=True,
                install_log=install_log or "Dependencies already installed; reusing cached node_modules.",
            )
            build_result = _run(["run", "build"])
            build_log = "\n".join(
                [build_result.stdout[-4000:], build_result.stderr[-4000:]]
            ).strip()
            built = (frontend_dir / "dist" / "index.html").is_file()
            build_success = build_result.returncode == 0 and built
            _update_job(
                status="completed" if build_success else "failed",
                phase="Build complete." if build_success else "Frontend build failed.",
                install_success=True,
                build_success=build_success,
                built=built,
                install_log=install_log or "Dependencies already installed; reusing cached node_modules.",
                build_log=build_log,
            )
        except Exception as error:
            _update_job(
                status="failed",
                phase="Build failed.",
                install_success=install_success,
                build_success=False,
                built=(frontend_dir / "dist" / "index.html").is_file(),
                install_log=install_log,
                build_log=str(error) if not build_log else f"{build_log}\n{error}",
            )

    threading.Thread(target=_run_build, name=f"frontend-build-{project_slug}", daemon=True).start()
    with _BUILD_JOBS_LOCK:
        return dict(_BUILD_JOBS[project_slug])


@app.get("/projects/{project_slug}/build", tags=["projects"])
def get_project_build_status(project_slug: str) -> dict[str, Any]:
    """Return the current frontend build status."""
    _resolve_project_dir(project_slug)
    with _BUILD_JOBS_LOCK:
        job = _BUILD_JOBS.get(project_slug)
        if job is None:
            raise HTTPException(status_code=404, detail="No frontend build has been started for this project")
        return dict(job)


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


def _premium_stage_file(project_slug: str, preview_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", preview_id):
        raise HTTPException(status_code=400, detail="Invalid premium design preview ID")
    stage_file = (PREMIUM_DESIGN_ROOT / project_slug / f"{preview_id}.json").resolve()
    if PREMIUM_DESIGN_ROOT.resolve() not in stage_file.parents:
        raise HTTPException(status_code=400, detail="Invalid premium design preview path")
    return stage_file


def _load_premium_stage(project_slug: str, preview_id: str) -> dict[str, Any]:
    stage_file = _premium_stage_file(project_slug, preview_id)
    if not stage_file.is_file():
        raise HTTPException(status_code=404, detail="Premium design preview not found or already discarded")
    try:
        stage = json.loads(stage_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=500, detail=f"Unable to read premium design preview: {error}") from error
    if not isinstance(stage, dict) or stage.get("project_slug") != project_slug:
        raise HTTPException(status_code=404, detail="Premium design preview does not belong to this project")
    if (
        not isinstance(stage.get("created_at"), (int, float))
        or not isinstance(stage.get("css"), str)
        or not isinstance(stage.get("direction"), dict)
    ):
        raise HTTPException(status_code=500, detail="Premium design preview metadata is invalid")
    if time.time() - stage["created_at"] > 7200:
        stage_file.unlink(missing_ok=True)
        raise HTTPException(status_code=410, detail="Premium design preview expired; create a new preview")
    return stage


def _render_premium_preview(
    project_slug: str,
    preview_id: str,
    file_path: str,
) -> Response:
    project_dir = _resolve_project_dir(project_slug)
    stage = _load_premium_stage(project_slug, preview_id)
    dist_dir = (project_dir / "frontend" / "dist").resolve()
    if not (dist_dir / "index.html").is_file():
        raise HTTPException(status_code=404, detail="Build the website before creating a premium design preview")

    requested_path = file_path or "index.html"
    target = (dist_dir / requested_path).resolve()
    if target != dist_dir and dist_dir not in target.parents:
        raise HTTPException(status_code=400, detail="Invalid premium preview asset path")
    if target.is_file() and target.name != "index.html":
        return FileResponse(target)
    if not target.is_file() and requested_path != "index.html":
        target = dist_dir / "index.html"

    source_html = target.read_text(encoding="utf-8")
    source_html = _rewrite_index_assets(
        source_html,
        f"/projects/{project_slug}/preview",
    )
    if "</head>" not in source_html:
        raise HTTPException(status_code=500, detail="Built website does not contain a valid HTML head element")
    style_tag = f'<style id="premium-design-preview">\n{stage["css"]}\n</style>\n'
    source_html = source_html.replace("</head>", f"{style_tag}</head>", 1)
    return HTMLResponse(content=source_html, media_type="text/html")


@app.post("/projects/{project_slug}/premium-design/preview", tags=["projects"])
def create_premium_design_preview(
    project_slug: str,
    request: PremiumDesignRequest,
) -> dict[str, Any]:
    """Stage prompt-aware visual enhancements without modifying generated project files."""
    project_dir = _resolve_project_dir(project_slug)
    frontend_dir = project_dir / "frontend"
    style_file = frontend_dir / "src" / "styles.css"
    if not style_file.is_file():
        raise HTTPException(status_code=400, detail="This project has no supported frontend stylesheet to enhance")
    if not (frontend_dir / "dist" / "index.html").is_file():
        raise HTTPException(status_code=409, detail="Build this project before creating a visual preview")

    user_prompt = request.user_prompt.strip() or project_slug.replace("_", " ")
    direction = premium_design_engine.create_art_direction(user_prompt, request.style)
    css = premium_design_engine.create_css(direction)
    validation_errors = premium_design_engine.validate_css(css)
    if validation_errors:
        raise HTTPException(status_code=500, detail={"message": "Premium styles failed visual validation", "errors": validation_errors})

    preview_id = secrets.token_urlsafe(18)
    stage_file = _premium_stage_file(project_slug, preview_id)
    stage_file.parent.mkdir(parents=True, exist_ok=True)
    stage = {
        "project_slug": project_slug,
        "created_at": time.time(),
        "base_css_sha256": hashlib.sha256(style_file.read_bytes()).hexdigest(),
        "css": css,
        "direction": direction,
    }
    temporary_stage = stage_file.with_suffix(".tmp")
    temporary_stage.write_text(json.dumps(stage), encoding="utf-8")
    os.replace(temporary_stage, stage_file)

    return {
        "preview_id": preview_id,
        "project_slug": project_slug,
        "preview_url": f"/projects/{project_slug}/premium-preview/{preview_id}",
        "direction": direction,
        "validation": {
            "passed": not validation_errors,
            "checks": [
                "CSS-only changes",
                "Responsive breakpoints",
                "Keyboard focus visibility",
                "Reduced-motion support",
                "No new remote fonts, images, or dependencies",
            ],
        },
    }


@app.get("/projects/{project_slug}/premium-preview/{preview_id}", tags=["projects"])
def premium_design_preview(project_slug: str, preview_id: str) -> Response:
    """Serve the staged visual preview while preserving the original built project."""
    return _render_premium_preview(project_slug, preview_id, "index.html")


@app.get("/projects/{project_slug}/premium-preview/{preview_id}/{file_path:path}", tags=["projects"])
def premium_design_preview_asset(
    project_slug: str,
    preview_id: str,
    file_path: str,
) -> Response:
    """Serve staged preview assets and SPA routes."""
    return _render_premium_preview(project_slug, preview_id, file_path)


@app.post("/projects/{project_slug}/premium-design/{preview_id}/accept", tags=["projects"])
def accept_premium_design(project_slug: str, preview_id: str) -> dict[str, Any]:
    """Apply approved CSS and keep it only if the frontend build and project checks pass."""
    project_dir = _resolve_project_dir(project_slug)
    stage_file = _premium_stage_file(project_slug, preview_id)
    stage = _load_premium_stage(project_slug, preview_id)
    frontend_dir = project_dir / "frontend"
    style_file = frontend_dir / "src" / "styles.css"
    dist_dir = frontend_dir / "dist"
    if not style_file.is_file() or not (dist_dir / "index.html").is_file():
        raise HTTPException(status_code=409, detail="Project source or built preview changed; build it and create a fresh design preview")

    original_css = style_file.read_text(encoding="utf-8")
    current_hash = hashlib.sha256(style_file.read_bytes()).hexdigest()
    if current_hash != stage.get("base_css_sha256"):
        raise HTTPException(status_code=409, detail="The stylesheet changed after preview. Create a fresh design preview before accepting.")

    css_addition = stage.get("css")
    validation_errors = premium_design_engine.validate_css(css_addition if isinstance(css_addition, str) else "")
    if validation_errors:
        raise HTTPException(status_code=500, detail={"message": "Staged CSS failed validation", "errors": validation_errors})
    try:
        updated_css = premium_design_engine.replace_css(original_css, css_addition)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise HTTPException(status_code=500, detail="Node/npm is not installed on this machine")

    with tempfile.TemporaryDirectory(prefix="premium-design-rollback-") as rollback_dir:
        backup_dist = Path(rollback_dir) / "dist"
        shutil.copytree(dist_dir, backup_dist)

        temporary_css = style_file.with_name(f"{style_file.name}.premium.tmp")
        temporary_css.write_text(updated_css, encoding="utf-8")
        os.replace(temporary_css, style_file)

        try:
            build_result = subprocess.run(
                [npm, "run", "build"],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=900,
                shell=False,
            )
        except subprocess.TimeoutExpired as error:
            build_result = None
            build_error = f"Frontend build timed out after {error.timeout} seconds"
        except OSError as error:
            build_result = None
            build_error = f"Unable to run frontend build: {error}"
        else:
            build_error = ""

        report = orchestrator.testing_agent.test_project(project_dir) if build_result and build_result.returncode == 0 else None
        active_css = premium_design_engine.active_premium_css(style_file.read_text(encoding="utf-8"))
        post_build_errors = (
            premium_design_engine.validate_css(active_css)
            if active_css
            else ["Accepted premium style block is missing from the stylesheet."]
        )
        build_succeeded = (
            build_result is not None
            and build_result.returncode == 0
            and (dist_dir / "index.html").is_file()
            and report is not None
            and report.is_valid
            and not post_build_errors
        )
        if not build_succeeded:
            style_file.write_text(original_css, encoding="utf-8")
            if dist_dir.exists():
                shutil.rmtree(dist_dir)
            shutil.copytree(backup_dist, dist_dir)
            if build_result is not None:
                details = "\n".join((build_result.stdout[-2500:], build_result.stderr[-2500:])).strip()
                if report is not None and not report.is_valid:
                    details += f"\nProject validation errors: {'; '.join(report.errors)}"
                if post_build_errors:
                    details += f"\nVisual validation errors: {'; '.join(post_build_errors)}"
            else:
                details = build_error
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Premium design was rolled back because build or validation failed. The existing website is unchanged.",
                    "details": details,
                },
            )

    stage_file.unlink(missing_ok=True)
    return {
        "accepted": True,
        "project_slug": project_slug,
        "personality": stage["direction"]["personality"],
        "functional_validation": orchestrator._serialize(report),
        "message": "Premium visual styles were applied and the frontend rebuilt successfully. Application source and backend behavior were unchanged.",
    }


@app.delete("/projects/{project_slug}/premium-design/{preview_id}", tags=["projects"])
def reject_premium_design(project_slug: str, preview_id: str) -> dict[str, Any]:
    """Discard a staged visual direction without changing project files."""
    _resolve_project_dir(project_slug)
    stage_file = _premium_stage_file(project_slug, preview_id)
    if not stage_file.is_file():
        raise HTTPException(status_code=404, detail="Premium design preview not found or already discarded")
    stage_file.unlink()
    return {"rejected": True, "project_slug": project_slug, "message": "Preview discarded; the existing project was not changed."}


@app.get("/projects/{project_slug}/test", tags=["projects"])
def test_generated_project(project_slug: str) -> dict[str, Any]:
    """Run automated testing checks on a generated project on demand."""
    project_dir = _resolve_project_dir(project_slug)
    report = orchestrator.testing_agent.test_project(project_dir)
    return orchestrator._serialize(report)


@app.post("/projects/{project_slug}/debug", tags=["projects"])
def debug_generated_project(project_slug: str) -> dict[str, Any]:
    """Run automated debugging and self-healing loop on a generated project."""
    project_dir = _resolve_project_dir(project_slug)
    test_report, debug_report = orchestrator.debugging_agent.debug_loop(project_dir)
    return {
        "testing_report": orchestrator._serialize(test_report),
        "debug_report": orchestrator._serialize(debug_report),
    }


@app.get("/projects/{project_slug}/security", tags=["projects"])
def audit_project_security(project_slug: str) -> dict[str, Any]:
    """Run automated security audit and vulnerability check on a generated project."""
    project_dir = _resolve_project_dir(project_slug)
    report = orchestrator.security_agent.audit_project(project_dir)
    return orchestrator._serialize(report)


@app.get("/projects/{project_slug}/deployment", tags=["projects"])
def get_deployment_config(project_slug: str) -> dict[str, Any]:
    """Retrieve production deployment artifacts, Dockerfiles, and instructions."""
    project_dir = _resolve_project_dir(project_slug)
    report = orchestrator.deployment_agent.prepare_deployment(project_dir, project_name=project_slug.replace("_", " ").title())
    return orchestrator._serialize(report)
