from __future__ import annotations

from typing import Protocol

from .code_generator import CodeGenerator, PromptProvider
from .code_schema import GeneratedFile


class BackendGenerator(CodeGenerator):
    """Generates backend code artifacts for Version 2."""

    def generate_files(self, prompt_provider: PromptProvider) -> list[GeneratedFile]:
        """Create backend files from the given prompt provider."""
        prompt = prompt_provider.get_prompt()
        return self._build_backend_files(prompt)

    def _build_backend_files(self, prompt: str) -> list[GeneratedFile]:
        """Construct the initial backend file list."""
        # TODO: implement backend generation using Ollama and structured prompts
        return [
            GeneratedFile(
                path="backend/app/main.py",
                content=self._backend_main_placeholder(),
            ),
            GeneratedFile(
                path="backend/app/api/router.py",
                content=self._backend_router_placeholder(),
            ),
        ]

    def _backend_main_placeholder(self) -> str:
        """Return a placeholder FastAPI main application."""
        return (
            "from fastapi import FastAPI\n"
            "\n"
            "app = FastAPI()\n"
            "\n"
            "@app.get('/')\n"
            "async def read_root() -> dict[str, str]:\n"
            "    return {'message': 'Generated backend is working'}\n"
        )

    def _backend_router_placeholder(self) -> str:
        """Return a placeholder API router file."""
        return (
            "from fastapi import APIRouter\n"
            "\n"
            "router = APIRouter()\n"
            "\n"
            "@router.get('/health')\n"
            "async def health_check() -> dict[str, str]:\n"
            "    return {'status': 'ok'}\n"
        )
