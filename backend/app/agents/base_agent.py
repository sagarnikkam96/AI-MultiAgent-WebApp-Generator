"""Base abstractions for AI agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Base interface for all agents in the system."""

    def __init__(self, name: str, description: str | None = None) -> None:
        """Initialize the agent with basic metadata."""
        self.name = name
        self.description = description

    @abstractmethod
    def analyze(self, user_prompt: str) -> Any:
        """Analyze a user prompt and return a structured result."""
        raise NotImplementedError
