"""
Portfolio service – builds portfolio sections from profile.
"""
from __future__ import annotations
import json

from app.ai.text_generator import generate_professional_summary


def build_portfolio_content(profile) -> dict:
    """Generate portfolio sections from Profile ORM object."""
    skills_by_category: dict[str, list[str]] = {}
    for skill in profile.skills:
        cat = skill.category or "General"
        skills_by_category.setdefault(cat, []).append(skill.name)

    about = profile.summary or generate_professional_summary({
        "full_name": profile.full_name,
        "skills": [s.name for s in profile.skills],
        "education": [e.to_dict() for e in profile.education],
        "experience": [x.to_dict() for x in profile.experience],
    })

    projects = [p.to_dict() for p in profile.projects]
    experience = [x.to_dict() for x in profile.experience]

    contact = {
        "email": profile.user.email if profile.user else "",
        "phone": profile.phone,
        "linkedin": profile.linkedin,
        "github": profile.github,
        "website": profile.website,
        "location": profile.location,
    }

    return {
        "about": about,
        "skills": skills_by_category,
        "projects": projects,
        "experience": experience,
        "contact": contact,
    }
