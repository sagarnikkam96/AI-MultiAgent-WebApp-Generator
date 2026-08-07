from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from ..code_generator.code_schema import GeneratedFile


class FileWriter:
    """Writes generated files safely to disk."""

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path).resolve()

    def write_files(self, files: Iterable[GeneratedFile]) -> list[Path]:
        """Write generated files to disk and return their created paths."""
        created_paths: list[Path] = []
        for generated_file in files:
            destination = self._resolve_destination(generated_file.path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(generated_file.content, encoding="utf-8")
            created_paths.append(destination)
        return created_paths

    def _resolve_destination(self, relative_path: str) -> Path:
        """Resolve a relative generated file path against the allowed base path."""
        normalized_path = Path(relative_path)
        if normalized_path.is_absolute():
            raise ValueError("Generated file path must be relative")

        resolved_path = (self.base_path / normalized_path).resolve()
        if self.base_path not in resolved_path.parents and resolved_path != self.base_path:
            raise ValueError("Unsafe file path detected")

        return resolved_path
