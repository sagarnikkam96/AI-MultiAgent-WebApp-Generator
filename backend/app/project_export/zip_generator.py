from __future__ import annotations

import shutil
from pathlib import Path


class ZipGenerator:
    """Creates a ZIP archive from a generated project directory."""

    def __init__(self, output_directory: str | Path | None = None) -> None:
        self.output_directory = Path(output_directory) if output_directory is not None else None

    def generate_zip(self, source_directory: str | Path, output_filename: str) -> Path:
        """Create a zip archive from the source directory."""
        source_path = Path(source_directory).resolve()
        if not source_path.is_dir():
            raise ValueError(f"Source directory does not exist: {source_path}")

        output_dir = self.output_directory or source_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        archive_path = output_dir / f"{output_filename}.zip"

        shutil.make_archive(str(archive_path.with_suffix("")), "zip", root_dir=str(source_path))
        return archive_path
