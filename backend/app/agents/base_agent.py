"""Base abstractions for AI agents."""

from __future__ import annotations

from typing import Any


class BaseAgent:
    """Base class for all AI agents in the system."""

    def __init__(self, name: str, description: str | None = None) -> None:
        """Initialize the agent with a name and optional description."""
        self.name = name
        self.description = description

    def process(self, input_data: Any) -> Any:
        """Process input data and return a result."""
        raise NotImplementedError
