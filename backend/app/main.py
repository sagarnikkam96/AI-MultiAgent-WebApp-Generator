"""FastAPI application entrypoint for the backend service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .agents.requirement_agent import RequirementAgent
from .agents.schemas import RequirementSchema


class AnalyzeRequest(BaseModel):
    """Request payload for requirement analysis."""

    user_prompt: str = Field(..., description="User prompt describing the project requirements")

app = FastAPI(
    title="AI Multi-Agent Web Application Generator Backend",
    version="0.1.0",
    description="Minimal FastAPI application for backend verification.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = RequirementAgent()


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    """Return the backend health response for startup verification."""
    return {
        "message": "AI Multi-Agent Web Application Generator Backend Running",
        "status": "success",
        "version": "0.1.0",
    }


@app.post("/analyze", tags=["requirements"], response_model=RequirementSchema)
def analyze_requirements(request: AnalyzeRequest) -> RequirementSchema:
    """Analyze a user prompt and return structured project requirements."""
    return agent.analyze(request.user_prompt)
