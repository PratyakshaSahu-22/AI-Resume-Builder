"""
Resume Builder routes – Generate, Edit, Preview, Download PDF.
"""
import json
from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for, send_file, current_app, Response
)
import io
from app import db
from app.models import Resume, User
from app.utils.jwt_helper import login_required
from app.services.resume_service import build_resume_content, analyse_resume
from app.services.pdf_service import generate_pdf_from_html
from app.utils.validators import sanitize_text

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/")
@login_required
def index():
    user_id = request.current_user_id
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.updated_at.desc()).all()
    return render_template("resume/index.html", resumes=resumes)


@resume_bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    user_id = request.current_user_id
    user = User.query.get_or_404(user_id)
    profile = user.profile

    if not profile:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("profile.index"))

    if request.method == "POST":
        job_description = sanitize_text(request.form.get("job_description", ""), 5000)

        # Build resume content via AI
        content_data = build_resume_content(profile)

        # Build plain text version for ML analysis
        resume_text = _dict_to_plaintext(content_data)

        # Run ML analysis
        analysis = analyse_resume(resume_text, job_description)

        # Persist to DB
        resume = Resume(
            user_id=user_id,
            title=request.form.get("title", "My Resume") or "My Resume",
            content=json.dumps(content_data),
            ats_score=analysis["ats"]["ats_score"],
            job_description=job_description,
            match_score=analysis["match"].get("match_score", 0.0),
            suggestions=json.dumps(analysis["suggestions"]),
        )
        db.session.add(resume)
        db.session.commit()

        flash("Resume generated successfully!", "success")
        return redirect(url_for("resume.edit", resume_id=resume.id))

    return render_template("resume/generate.html", profile=profile)


@resume_bp.route("/<int:resume_id>/edit", methods=["GET", "POST"])
@login_required
def edit(resume_id: int):
    user_id = request.current_user_id
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first_or_404()

    if request.method == "POST":
        resume.title = sanitize_text(request.form.get("title", resume.title), 200)
        # Save edited content sections back
        content_data = json.loads(resume.content or "{}")
        content_data["summary"] = sanitize_text(request.form.get("summary", ""), 2000)

        # Handle skill edits (comma-separated)
        edited_skills = request.form.get("skills_text", "")
        if edited_skills:
            skill_names = [s.strip() for s in edited_skills.split(",") if s.strip()]
            content_data["skills"] = [{"name": s, "category": "", "proficiency": ""} for s in skill_names]

        resume.content = json.dumps(content_data)
        resume.job_description = sanitize_text(request.form.get("job_description", resume.job_description or ""), 5000)

        # Re-run ATS
        resume_text = _dict_to_plaintext(content_data)
        analysis = analyse_resume(resume_text, resume.job_description or "")
        resume.ats_score = analysis["ats"]["ats_score"]
        resume.match_score = analysis["match"].get("match_score", 0.0)
        resume.suggestions = json.dumps(analysis["suggestions"])

        db.session.commit()
        flash("Resume saved.", "success")
        return redirect(url_for("resume.edit", resume_id=resume.id))

    content_data = json.loads(resume.content or "{}")
    suggestions = json.loads(resume.suggestions or "[]")
    skills_text = ", ".join(s.get("name", "") for s in content_data.get("skills", []))
    return render_template(
        "resume/edit.html",
        resume=resume,
        content=content_data,
        suggestions=suggestions,
        skills_text=skills_text,
    )


@resume_bp.route("/<int:resume_id>/preview")
@login_required
def preview(resume_id: int):
    user_id = request.current_user_id
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first_or_404()
    user = User.query.get(user_id)
    content_data = json.loads(resume.content or "{}")
    suggestions = json.loads(resume.suggestions or "[]")
    return render_template(
        "resume/preview.html",
        resume=resume,
        content=content_data,
        user=user,
        suggestions=suggestions,
    )


@resume_bp.route("/<int:resume_id>/download")
@login_required
def download(resume_id: int):
    user_id = request.current_user_id
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first_or_404()
    user = User.query.get(user_id)
    content_data = json.loads(resume.content or "{}")

    html_content = render_template(
        "resume/pdf_template.html",
        resume=resume,
        content=content_data,
        user=user,
    )
    try:
        pdf_bytes = generate_pdf_from_html(html_content)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="resume_{resume_id}.pdf"'
            },
        )
    except RuntimeError as e:
        flash(f"PDF generation unavailable: {e}. Please install weasyprint or xhtml2pdf.", "warning")
        return redirect(url_for("resume.preview", resume_id=resume_id))


@resume_bp.route("/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete(resume_id: int):
    user_id = request.current_user_id
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first_or_404()
    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted.", "info")
    return redirect(url_for("resume.index"))


def _dict_to_plaintext(content: dict) -> str:
    """Flatten resume content dict to plain text for ML analysis."""
    parts = []
    if content.get("summary"):
        parts.append("SUMMARY\n" + content["summary"])
    if content.get("skills"):
        skill_names = [s.get("name", "") for s in content["skills"]]
        parts.append("SKILLS\n" + ", ".join(skill_names))
    if content.get("education"):
        edus = [f"{e.get('degree','')} {e.get('field_of_study','')} {e.get('institution','')}" for e in content["education"]]
        parts.append("EDUCATION\n" + "\n".join(edus))
    if content.get("experience"):
        exps = [f"{x.get('role','')} at {x.get('company','')} - {x.get('description','')}" for x in content["experience"]]
        parts.append("EXPERIENCE\n" + "\n".join(exps))
    if content.get("projects"):
        projs = [f"{p.get('title','')} - {p.get('enhanced') or p.get('description','')}" for p in content["projects"]]
        parts.append("PROJECTS\n" + "\n".join(projs))
    if content.get("certifications"):
        certs = [f"{c.get('name','')} from {c.get('issuing_org','')}" for c in content["certifications"]]
        parts.append("CERTIFICATIONS\n" + "\n".join(certs))
    personal = content.get("personal", {})
    if personal.get("linkedin"):
        parts.append("linkedin " + personal["linkedin"])
    if personal.get("github"):
        parts.append("github " + personal["github"])
    return "\n\n".join(parts)
