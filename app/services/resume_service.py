"""
Resume service – orchestrates AI/ML modules to build resume content.
"""
from __future__ import annotations
import json

from app.ai.text_generator import generate_professional_summary, enhance_project_description
from app.ml.ats_scorer import predict_ats_score, match_resume_to_jd, generate_improvement_suggestions, classify_resume


def build_resume_content(profile) -> dict:
    """
    Assemble resume content dict from a Profile ORM object.
    """
    profile_data = _profile_to_dict(profile)

    # Generate AI summary if user has none (None or empty string both trigger generation)
    summary = profile.summary if profile.summary else generate_professional_summary(profile_data)

    # Enhance project descriptions
    projects_data = []
    for proj in profile.projects:
        enhanced = proj.ai_enhanced_description or enhance_project_description(
            proj.title, proj.description or "", proj.tech_stack or ""
        )
        p = proj.to_dict()
        p["enhanced"] = enhanced
        projects_data.append(p)

    return {
        "summary": summary,
        "skills": [s.to_dict() for s in profile.skills],
        "education": [e.to_dict() for e in profile.education],
        "experience": [x.to_dict() for x in profile.experience],
        "projects": projects_data,
        "certifications": [c.to_dict() for c in profile.certifications],
        "personal": profile.to_dict(),
    }


def analyse_resume(resume_text: str, job_description: str = "") -> dict:
    """Run all ML analyses and return combined result."""
    ats = predict_ats_score(resume_text, job_description)
    suggestions = generate_improvement_suggestions(resume_text, ats)
    match = match_resume_to_jd(resume_text, job_description) if job_description else {}
    category = classify_resume(resume_text)
    return {
        "ats": ats,
        "suggestions": suggestions,
        "match": match,
        "category": category,
    }


def _profile_to_dict(profile) -> dict:
    return {
        "full_name": profile.full_name,
        "skills": [s.name for s in profile.skills],
        "education": [e.to_dict() for e in profile.education],
        "experience": [x.to_dict() for x in profile.experience],
        "projects": [p.to_dict() for p in profile.projects],
    }
