"""Deployment Agent for preparing production artifacts and deployment configurations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base_agent import BaseAgent
from .schemas import DeploymentReport, DeploymentArtifact


class DeploymentAgent(BaseAgent):
    """Agent that prepares production Dockerfiles, docker-compose, and deployment documentation."""

    def __init__(self, name: str = "deployment_agent") -> None:
        super().__init__(name=name, description="Prepares production build configurations, containers, and deployment instructions")

    def analyze(self, user_prompt: str) -> Any:
        return user_prompt

    def prepare_deployment(self, project_dir: Path | str, project_name: str = "Web App") -> DeploymentReport:
        """Generate and write production deployment artifacts to the project directory."""
        dir_path = Path(project_dir).resolve()
        artifacts: list[DeploymentArtifact] = []

        if dir_path.is_dir():
            # 1. Backend Dockerfile
            backend_dockerfile = dir_path / "backend" / "Dockerfile"
            backend_dockerfile_content = (
                "FROM python:3.11-slim\n\n"
                "WORKDIR /app\n\n"
                "ENV PYTHONDONTWRITEBYTECODE=1 \\\n"
                "    PYTHONUNBUFFERED=1\n\n"
                "RUN apt-get update && apt-get install -y --no-install-recommends \\\n"
                "    gcc libpq-dev && \\\n"
                "    rm -rf /var/lib/apt/lists/*\n\n"
                "COPY requirements.txt .\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n\n"
                "COPY . .\n\n"
                "EXPOSE 8000\n\n"
                "CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
            )
            backend_dockerfile.parent.mkdir(parents=True, exist_ok=True)
            backend_dockerfile.write_text(backend_dockerfile_content, encoding="utf-8")
            artifacts.append(DeploymentArtifact(
                filename="Dockerfile",
                path="backend/Dockerfile",
                description="Production container image specification for FastAPI backend",
            ))

            # 2. Frontend Dockerfile
            frontend_dockerfile = dir_path / "frontend" / "Dockerfile"
            frontend_dockerfile_content = (
                "# Stage 1: Build React Application\n"
                "FROM node:20-alpine AS build\n"
                "WORKDIR /app\n"
                "COPY package*.json ./\n"
                "RUN npm install\n"
                "COPY . .\n"
                "RUN npm run build\n\n"
                "# Stage 2: Serve with Nginx\n"
                "FROM nginx:alpine\n"
                "COPY --from=build /app/dist /usr/share/nginx/html\n"
                "EXPOSE 80\n"
                "CMD [\"nginx\", \"-g\", \"daemon off;\"]\n"
            )
            frontend_dockerfile.parent.mkdir(parents=True, exist_ok=True)
            frontend_dockerfile.write_text(frontend_dockerfile_content, encoding="utf-8")
            artifacts.append(DeploymentArtifact(
                filename="Dockerfile",
                path="frontend/Dockerfile",
                description="Multi-stage production build container for React frontend with Nginx",
            ))

            # 3. Root docker-compose.yml
            docker_compose = dir_path / "docker-compose.yml"
            docker_compose_content = (
                "version: '3.8'\n\n"
                "services:\n"
                "  backend:\n"
                "    build: ./backend\n"
                "    ports:\n"
                "      - '8000:8000'\n"
                "    environment:\n"
                "      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app_db\n"
                "      - SECRET_KEY=production-secret-key-replace-in-env\n"
                "    depends_on:\n"
                "      db:\n"
                "        condition: service_healthy\n\n"
                "  frontend:\n"
                "    build: ./frontend\n"
                "    ports:\n"
                "      - '80:80'\n"
                "    depends_on:\n"
                "      - backend\n\n"
                "  db:\n"
                "    image: postgres:15-alpine\n"
                "    environment:\n"
                "      - POSTGRES_USER=postgres\n"
                "      - POSTGRES_PASSWORD=postgres\n"
                "      - POSTGRES_DB=app_db\n"
                "    volumes:\n"
                "      - pgdata:/var/lib/postgresql/data\n"
                "    ports:\n"
                "      - '5432:5432'\n"
                "    healthcheck:\n"
                "      test: ['CMD-SHELL', 'pg_isready -U postgres']\n"
                "      interval: 5s\n"
                "      timeout: 5s\n"
                "      retries: 5\n\n"
                "volumes:\n"
                "  pgdata:\n"
            )
            docker_compose.write_text(docker_compose_content, encoding="utf-8")
            artifacts.append(DeploymentArtifact(
                filename="docker-compose.yml",
                path="docker-compose.yml",
                description="Multi-container configuration for frontend, FastAPI backend, and PostgreSQL database",
            ))

            # 4. Environment Template .env.example
            env_example = dir_path / ".env.example"
            env_content = (
                "# Application Environment Configuration\n"
                "PROJECT_NAME=" + project_name + "\n"
                "ENVIRONMENT=production\n"
                "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app_db\n"
                "SECRET_KEY=change-this-to-a-secure-random-secret-key\n"
                "CORS_ORIGINS=http://localhost:5173,http://localhost:3000\n"
                "PORT=8000\n"
            )
            env_example.write_text(env_content, encoding="utf-8")
            artifacts.append(DeploymentArtifact(
                filename=".env.example",
                path=".env.example",
                description="Environment variable configuration template",
            ))

            # 5. Production DEPLOYMENT.md
            deploy_md = dir_path / "DEPLOYMENT.md"
            deploy_md_content = (
                f"# Deployment Guide - {project_name}\n\n"
                "This application is prepared for local development, containerized deployment, or cloud hosting.\n\n"
                "## Option 1: Docker Compose (Recommended)\n"
                "Run the complete full-stack environment with a single command:\n"
                "```bash\n"
                "docker compose up --build\n"
                "```\n"
                "- Frontend: http://localhost:80\n"
                "- Backend API: http://localhost:8000\n"
                "- Swagger Docs: http://localhost:8000/docs\n\n"
                "## Option 2: Local Development\n"
                "### Backend:\n"
                "```bash\n"
                "cd backend\n"
                "pip install -r requirements.txt\n"
                "python -m uvicorn app.main:app --reload --port 8000\n"
                "```\n\n"
                "### Frontend:\n"
                "```bash\n"
                "cd frontend\n"
                "npm install\n"
                "npm run dev\n"
                "```\n\n"
                "## Option 3: Cloud Deployment (Render / Vercel / Railway)\n"
                "- **Frontend**: Connect `frontend/` folder to Vercel, Netlify, or Render Static Site.\n"
                "- **Backend**: Connect `backend/` folder to Render Web Service or Railway with Python environment.\n"
                "- **Database**: Attach managed PostgreSQL instance and set `DATABASE_URL` environment variable.\n"
            )
            deploy_md.write_text(deploy_md_content, encoding="utf-8")
            artifacts.append(DeploymentArtifact(
                filename="DEPLOYMENT.md",
                path="DEPLOYMENT.md",
                description="Comprehensive step-by-step production deployment documentation",
            ))

        env_vars = [
            "DATABASE_URL (e.g. postgresql://user:pass@host:5432/dbname)",
            "SECRET_KEY (JWT encryption secret)",
            "CORS_ORIGINS (comma-separated allowed origins)",
            "ENVIRONMENT (development / production)",
        ]

        instructions = (
            "To deploy containerized:\n"
            "1. Copy .env.example to .env and configure secrets.\n"
            "2. Run 'docker compose up --build' in the project root.\n"
            "3. Access frontend at http://localhost:80 and backend API at http://localhost:8000."
        )

        status_message = "Deployment preparation completed; actual deployment requires configured deployment environment."

        return DeploymentReport(
            ready=True,
            artifacts=artifacts,
            environment_variables=env_vars,
            instructions=instructions,
            status_message=status_message,
        )
