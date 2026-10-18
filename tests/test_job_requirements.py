"""Tests for must-have parsing and filtering (no vector DB)."""

from job_matcher import (
    MustHaveRequirements,
    extract_required_skills,
    meets_must_have,
    parse_must_have_requirements,
    parse_must_have_years,
)


def test_parse_must_have_years_plus_and_minimum() -> None:
    assert parse_must_have_years("Need 5+ years Python") == 5
    assert parse_must_have_years("Minimum 3 years experience") == 3


def test_required_skills_and_semantics() -> None:
    jd = "5+ years Python. Required: Python, Django."
    reqs = parse_must_have_requirements(jd)
    assert reqs.min_years == 5
    assert extract_required_skills(jd) == ["Python", "Django"]

    pass_meta = {
        "experience_years": 6,
        "skills": "Python, Django, REST",
    }
    fail_years = {"experience_years": 3, "skills": "Python, Django"}
    fail_skill = {"experience_years": 6, "skills": "Python only"}

    assert meets_must_have(pass_meta, reqs) is True
    assert meets_must_have(fail_years, reqs) is False
    assert meets_must_have(fail_skill, reqs) is False


def test_no_required_block_skips_skill_and_filter() -> None:
    jd = "Senior Python developer with machine learning background."
    reqs = parse_must_have_requirements(jd)
    assert reqs.required_skills == []
    meta = {"experience_years": -1, "skills": ""}
    assert meets_must_have(meta, reqs) is True


def test_unknown_years_fails_when_years_required() -> None:
    reqs = MustHaveRequirements(min_years=5, required_skills=[], hybrid_skills=[])
    assert meets_must_have({"experience_years": -1, "skills": "Python"}, reqs) is False
