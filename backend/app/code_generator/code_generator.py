from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from ..llm.ollama_client import OllamaClient
from .code_schema import GeneratedFile


class PromptProvider(Protocol):
    """Protocol for objects that provide prompts to the code generator."""

    def get_prompt(self) -> str:
        ...


class CodeGenerator(ABC):
    """Base class for code generators that use the Ollama client."""

    def __init__(self, ollama_client: OllamaClient | None = None) -> None:
        self.ollama_client = ollama_client or OllamaClient()

    @abstractmethod
    def generate_files(self, prompt_provider: PromptProvider) -> list[GeneratedFile]:
        """Generate a set of files based on the provided prompt provider."""
        raise NotImplementedError

    def _generate_text(self, prompt: str) -> str:
        """Delegate text generation to the Ollama client."""
        return self.ollama_client.generate(prompt)
