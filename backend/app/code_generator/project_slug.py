from __future__ import annotations

import re


def project_slug(value: str) -> str:
    """Create the canonical generated-project directory name."""
    parts = re.findall(r"[a-z0-9]+", value.casefold())
    return "_".join(parts[:5])[:50] or "generated_project"
