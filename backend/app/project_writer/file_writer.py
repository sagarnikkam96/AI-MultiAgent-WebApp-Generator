from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from ..code_generator.code_schema import GeneratedFile
import json
import re


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
            content_to_write = generated_file.content

            # Special handling and validation for package.json
            if str(generated_file.path).endswith("package.json"):
                # Debug printing of the raw LLM response to aid debugging
                print("PACKAGE_JSON_RESPONSE_START")
                print(content_to_write)
                print("PACKAGE_JSON_RESPONSE_END")

                # Remove Markdown fences if present
                content_no_fences = re.sub(r'```(?:json)?\n', '', content_to_write, flags=re.IGNORECASE)
                content_no_fences = re.sub(r'```\s*$', '', content_no_fences, flags=re.MULTILINE)

                # Try to extract the first top-level JSON object from the response
                start = content_no_fences.find("{")
                end = content_no_fences.rfind("}")
                if start == -1 or end == -1 or end <= start:
                    raise ValueError("Generated package.json does not contain a JSON object.")

                candidate = content_no_fences[start : end + 1].strip()

                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Failed to parse generated package.json: {exc.msg} (line {exc.lineno} col {exc.colno})")

                # Serialize with stable formatting before writing
                content_to_write = json.dumps(parsed, indent=2)

            destination.write_text(content_to_write, encoding="utf-8")
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
