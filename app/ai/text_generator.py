"""
AI Module: Professional Summary & Project Description Generation.
Uses template-based NLG with NLTK sentence scoring when available.
No external LLM API required.
"""
from __future__ import annotations
import random


# ─── Summary templates ───────────────────────────────────────────────────────
SUMMARY_TEMPLATES = [
    (
        "A highly motivated {role} with hands-on experience in {top_skills}. "
        "Currently pursuing {degree} from {institution}, with a strong passion for "
        "building scalable and impactful software solutions."
    ),
    (
        "Enthusiastic and detail-oriented {role} skilled in {top_skills}. "
        "Seeking to leverage academic knowledge from {institution} and practical "
        "project experience to contribute to a forward-thinking organization."
    ),
    (
        "Dedicated {role} with a solid foundation in {top_skills}, gained through "
        "academic training at {institution} and hands-on project work. "
        "Eager to apply technical expertise to solve real-world problems."
    ),
]

# ─── Project enhancement verbs ───────────────────────────────────────────────
ACTION_VERBS = [
    "Designed", "Developed", "Implemented", "Built", "Architected",
    "Engineered", "Optimized", "Deployed", "Integrated", "Automated",
    "Streamlined", "Enhanced", "Created", "Configured", "Managed",
]


def generate_professional_summary(profile_data: dict) -> str:
    """
    Generate a professional summary from profile data dict.
    Keys expected: full_name, skills (list), education (list of dicts), experience (list)
    """
    skills: list[str] = profile_data.get("skills", [])
    education: list[dict] = profile_data.get("education", [])
    experience: list[dict] = profile_data.get("experience", [])

    # Determine role
    if experience:
        role = experience[0].get("role", "Software Developer")
    else:
        role = "Software Developer / Computer Science Student"

    # Top 3–5 skills
    top_skills_list = skills[:5] if skills else ["Python", "Machine Learning", "Web Development"]
    top_skills = ", ".join(top_skills_list[:-1]) + (
        f" and {top_skills_list[-1]}" if len(top_skills_list) > 1 else top_skills_list[0]
    )

    # Education
    degree = institution = "their institution"
    if education:
        edu = education[0]
        degree = f"{edu.get('degree', 'B.Tech')} in {edu.get('field_of_study', 'Computer Science')}"
        institution = edu.get("institution", "their institution")

    template = random.choice(SUMMARY_TEMPLATES)
    summary = template.format(
        role=role,
        top_skills=top_skills,
        degree=degree,
        institution=institution,
    )
    return summary


def enhance_project_description(title: str, description: str, tech_stack: str) -> str:
    """
    Improve a project description using action verbs and structured sentences.
    Returns an enhanced paragraph.
    """
    if not description:
        description = f"A project focused on {title}."

    techs = [t.strip() for t in (tech_stack or "").split(",") if t.strip()]
    tech_str = ", ".join(techs[:4]) if techs else "modern technologies"

    verb = random.choice(ACTION_VERBS)
    lines = [
        f"{verb} '{title}' using {tech_str}.",
        _clean_sentence(description),
    ]

    if techs:
        lines.append(
            f"The project demonstrates proficiency in {', '.join(techs[:3])}, "
            "showcasing the ability to build and deploy production-ready solutions."
        )

    return " ".join(lines)


def _clean_sentence(text: str) -> str:
    """Ensure sentence ends with a period and is properly capitalised."""
    text = text.strip()
    if text and not text.endswith((".", "!", "?")):
        text += "."
    if text:
        text = text[0].upper() + text[1:]
    return text


def generate_cover_letter(profile_data: dict, company: str, job_role: str) -> str:
    """
    Generate a personalised cover letter.
    """
    name = profile_data.get("full_name", "Candidate")
    skills = profile_data.get("skills", [])[:5]
    education = profile_data.get("education", [])
    experience = profile_data.get("experience", [])
    projects = profile_data.get("projects", [])

    edu_line = ""
    if education:
        edu = education[0]
        edu_line = (
            f"I am currently pursuing my {edu.get('degree', 'degree')} in "
            f"{edu.get('field_of_study', 'Computer Science')} from "
            f"{edu.get('institution', 'my institution')}."
        )

    skill_line = ""
    if skills:
        skill_line = f"My core competencies include {', '.join(skills[:-1])} and {skills[-1]}." if len(skills) > 1 else f"I am skilled in {skills[0]}."

    exp_line = ""
    if experience:
        exp = experience[0]
        exp_line = (
            f"Previously, I worked as {exp.get('role', 'a developer')} at "
            f"{exp.get('company', 'a company')}, where I "
            f"{exp.get('description', 'gained valuable industry experience')[:120]}."
        )

    project_line = ""
    if projects:
        proj = projects[0]
        project_line = (
            f"One of my key projects, '{proj.get('title', '')}', involved "
            f"{(proj.get('description') or proj.get('ai_enhanced_description') or 'building a full-stack application')[:150]}."
        )

    letter = f"""Dear Hiring Manager,

I am writing to express my enthusiastic interest in the {job_role} position at {company}. \
{edu_line}

{skill_line} {exp_line}

{project_line} I am particularly drawn to {company} because of its commitment to innovation \
and impact, and I am confident that my technical background aligns well with the requirements \
of the {job_role} role.

I am eager to contribute to your team and would welcome the opportunity to discuss how my \
skills and experiences can benefit {company}. Thank you for considering my application. \
I look forward to the possibility of working with you.

Sincerely,
{name}"""

    return letter
