"""Project-root-relative paths for resume files."""

from __future__ import annotations

from pathlib import Path

from embedding_utils import PROJECT_ROOT


def relative_resume_path(source: str, project_root: Path | None = None) -> str:
    """Return resume path relative to project root (e.g. Resume/file.pdf)."""
    root = (project_root or PROJECT_ROOT).resolve()
    path = Path(source)
    if path.is_absolute():
        return str(path.resolve().relative_to(root)).replace("\\", "/")
    return str(path).replace("\\", "/")


def resume_path_from_metadata(meta: dict, project_root: Path | None = None) -> str:
    stored = meta.get("resume_path")
    if stored:
        return str(stored)
    fallback = meta.get("path") or meta.get("source") or "unknown"
    if fallback == "unknown":
        return fallback
    return relative_resume_path(str(fallback), project_root)
