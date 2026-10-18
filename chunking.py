"""Section-aware resume chunking with recursive fallback."""

from __future__ import annotations

import re
from typing import Literal

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

SectionName = Literal[
    "Summary",
    "Skills",
    "Experience",
    "Education",
    "Projects",
    "Certifications",
    "Contact",
    "Other",
]

SECTION_HEADER_LINE = re.compile(
    r"^(?:Education|Experience|Work\s*Experience|Skills|Summary|Projects|Certifications|Contact)\s*$",
    re.IGNORECASE,
)

# Shared with resume_rag metadata parsing (multiline section boundaries).
SECTION_HEADERS = SECTION_HEADER_LINE

DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50


def is_section_header_line(line: str) -> bool:
    return bool(SECTION_HEADER_LINE.match(line.strip()))


def canonical_section_name(header_line: str) -> SectionName:
    normalized = header_line.strip().lower()
    if normalized.startswith("skill"):
        return "Skills"
    if "experience" in normalized or normalized == "work":
        return "Experience"
    if normalized.startswith("edu"):
        return "Education"
    if normalized.startswith("summary"):
        return "Summary"
    if normalized.startswith("project"):
        return "Projects"
    if normalized.startswith("cert"):
        return "Certifications"
    if normalized.startswith("contact"):
        return "Contact"
    return "Other"


def resume_has_section_headers(text: str) -> bool:
    for line in text.split("\n"):
        if is_section_header_line(line):
            return True
    return False


def split_text_into_sections(text: str) -> list[tuple[SectionName, str]]:
    """Split resume text into (section_name, body) pairs."""
    sections: list[tuple[SectionName, str]] = []
    current_section: SectionName = "Other"
    current_lines: list[str] = []

    def flush() -> None:
        if current_lines:
            body = "\n".join(current_lines).strip()
            if body:
                sections.append((current_section, body))

    for line in text.split("\n"):
        stripped = line.strip()
        if is_section_header_line(stripped):
            flush()
            current_section = canonical_section_name(stripped)
            current_lines = []
        else:
            current_lines.append(line)
    flush()
    return sections


def chunk_resume_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    base_metadata: dict[str, str] | None = None,
) -> list[Document]:
    """
    Chunk resume text by section when headers exist; otherwise recursive split on full text.
    """
    stripped = text.strip()
    if not stripped:
        raise ValueError("Cannot chunk empty resume text")

    meta_base = dict(base_metadata or {})
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks: list[Document] = []

    if not resume_has_section_headers(stripped):
        for piece in splitter.split_text(stripped):
            if not piece.strip():
                continue
            chunks.append(
                Document(
                    page_content=piece,
                    metadata={**meta_base, "section": "Other"},
                )
            )
    else:
        for section_name, section_body in split_text_into_sections(stripped):
            for piece in splitter.split_text(section_body):
                if not piece.strip():
                    continue
                chunks.append(
                    Document(
                        page_content=piece,
                        metadata={**meta_base, "section": section_name},
                    )
                )

    if not chunks:
        raise ValueError("Chunking produced no output for non-empty resume text")
    return chunks
