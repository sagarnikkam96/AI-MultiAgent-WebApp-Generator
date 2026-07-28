"""FastAPI application entrypoint for the backend service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    """Return the backend health response for startup verification."""
    return {
        "message": "AI Multi-Agent Web Application Generator Backend Running",
        "status": "success",
        "version": "0.1.0",
    }
