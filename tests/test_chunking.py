"""Tests for section-aware resume chunking."""

from chunking import chunk_resume_text, resume_has_section_headers, split_text_into_sections


SAMPLE_RESUME = """
Jane Doe
Summary
Backend engineer with 6+ years experience.

Skills
Python, Django, PostgreSQL

Experience
Acme Corp — built APIs with Python and Django.

Education
B.Tech Computer Science
"""


def test_detects_section_headers() -> None:
    assert resume_has_section_headers(SAMPLE_RESUME) is True


def test_split_sections_do_not_mix_skills_and_experience() -> None:
    sections = split_text_into_sections(SAMPLE_RESUME)
    names = [name for name, _ in sections]
    assert "Skills" in names
    assert "Experience" in names
    skills_body = next(body for name, body in sections if name == "Skills")
    experience_body = next(body for name, body in sections if name == "Experience")
    assert "Python" in skills_body
    assert "Acme Corp" in experience_body
    assert "Acme Corp" not in skills_body


def test_chunks_tagged_with_section_metadata() -> None:
    chunks = chunk_resume_text(SAMPLE_RESUME)
    sections = {c.metadata.get("section") for c in chunks}
    assert "Skills" in sections or "Experience" in sections
    for chunk in chunks:
        assert chunk.metadata.get("section")
        assert chunk.page_content.strip()


def test_no_headers_uses_other_section() -> None:
    plain = "Jane Doe\nBuilt systems with Python for many years.\n" * 20
    assert resume_has_section_headers(plain) is False
    chunks = chunk_resume_text(plain)
    assert all(c.metadata.get("section") == "Other" for c in chunks)
