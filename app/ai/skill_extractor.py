"""
AI Module: Skill Extraction using spaCy + keyword matching.
"""
from __future__ import annotations

# ── Common tech skill keywords (can be extended) ─────────────────────────────
TECH_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "rust", "swift", "kotlin", "php", "r", "scala", "perl", "matlab",
    "html", "css", "react", "angular", "vue", "node.js", "flask", "django",
    "fastapi", "spring", "laravel", "express",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ansible",
    "git", "github", "gitlab", "linux", "bash", "powershell",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "seaborn", "tableau", "power bi",
    "agile", "scrum", "jira", "figma", "photoshop",
}

SOFT_SKILLS = {
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "presentation", "project management",
}


def extract_skills_spacy(text: str) -> dict[str, list[str]]:
    """
    Extract skills from text.
    Uses spaCy if available, falls back to keyword matching.
    Returns {"technical": [...], "soft": [...]}
    """
    lower = text.lower()
    found_tech: list[str] = []
    found_soft: list[str] = []

    # Keyword matching (always runs)
    for skill in TECH_SKILLS:
        if skill in lower:
            found_tech.append(skill.title())
    for skill in SOFT_SKILLS:
        if skill in lower:
            found_soft.append(skill.title())

    # spaCy NER enrichment (optional – noun chunks)
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        for chunk in doc.noun_chunks:
            token = chunk.text.lower().strip()
            if token in TECH_SKILLS and chunk.text.title() not in found_tech:
                found_tech.append(chunk.text.title())
    except Exception:
        pass  # spaCy not available – keyword results already populated

    return {
        "technical": list(dict.fromkeys(found_tech)),   # preserve order, dedupe
        "soft": list(dict.fromkeys(found_soft)),
    }


def rank_skills_by_frequency(text: str, skills: list[str]) -> list[tuple[str, int]]:
    """Return (skill, count) sorted by frequency in text."""
    lower = text.lower()
    ranked = [(s, lower.count(s.lower())) for s in skills]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked
