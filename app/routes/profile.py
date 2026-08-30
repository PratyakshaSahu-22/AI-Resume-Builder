"""
Profile CRUD routes.
"""
import os
from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for, current_app
)
from werkzeug.utils import secure_filename
from app import db
from app.models import Profile, Education, Skill, Project, Experience, Certification, User
from app.utils.jwt_helper import login_required
from app.utils.validators import (
    sanitize_string, sanitize_text, is_valid_url, allowed_file
)

profile_bp = Blueprint("profile", __name__)


def _get_profile(user_id: int) -> Profile:
    user = User.query.get_or_404(user_id)
    if not user.profile:
        profile = Profile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return user.profile


# ─── Personal Details ────────────────────────────────────────────────────────
@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = request.current_user_id
    profile = _get_profile(user_id)

    if request.method == "POST":
        profile.full_name = sanitize_string(request.form.get("full_name", ""), 150)
        profile.phone = sanitize_string(request.form.get("phone", ""), 20)
        profile.location = sanitize_string(request.form.get("location", ""), 200)
        profile.linkedin = sanitize_string(request.form.get("linkedin", ""), 300)
        profile.github = sanitize_string(request.form.get("github", ""), 300)
        profile.website = sanitize_string(request.form.get("website", ""), 300)
        profile.summary = sanitize_text(request.form.get("summary", ""), 2000)

        # Profile picture upload
        if "picture" in request.files:
            f = request.files["picture"]
            if f and f.filename and allowed_file(f.filename, {"jpg", "jpeg", "png", "webp"}):
                filename = secure_filename(f"{user_id}_{f.filename}")
                upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                f.save(upload_path)
                profile.profile_picture = f"/static/uploads/{filename}"

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile.index"))

    user = User.query.get(user_id)
    return render_template("profile/index.html", profile=profile, user=user)


# ─── Education ───────────────────────────────────────────────────────────────
@profile_bp.route("/education", methods=["GET", "POST"])
@login_required
def education():
    user_id = request.current_user_id
    profile = _get_profile(user_id)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            edu = Education(
                profile_id=profile.id,
                institution=sanitize_string(request.form.get("institution", ""), 200),
                degree=sanitize_string(request.form.get("degree", ""), 200),
                field_of_study=sanitize_string(request.form.get("field_of_study", ""), 200),
                start_year=_safe_int(request.form.get("start_year")),
                end_year=_safe_int(request.form.get("end_year")),
                grade=sanitize_string(request.form.get("grade", ""), 50),
                description=sanitize_text(request.form.get("description", ""), 1000),
            )
            db.session.add(edu)
            db.session.commit()
            flash("Education entry added.", "success")
        elif action == "delete":
            edu_id = int(request.form.get("edu_id", 0))
            edu = Education.query.filter_by(id=edu_id, profile_id=profile.id).first()
            if edu:
                db.session.delete(edu)
                db.session.commit()
                flash("Education entry removed.", "info")
        return redirect(url_for("profile.education"))

    return render_template("profile/education.html", profile=profile)


# ─── Skills ──────────────────────────────────────────────────────────────────
@profile_bp.route("/skills", methods=["GET", "POST"])
@login_required
def skills():
    user_id = request.current_user_id
    profile = _get_profile(user_id)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            skill = Skill(
                profile_id=profile.id,
                name=sanitize_string(request.form.get("name", ""), 100),
                category=sanitize_string(request.form.get("category", ""), 100),
                proficiency=sanitize_string(request.form.get("proficiency", ""), 50),
            )
            db.session.add(skill)
            db.session.commit()
            flash("Skill added.", "success")
        elif action == "delete":
            sid = int(request.form.get("skill_id", 0))
            skill = Skill.query.filter_by(id=sid, profile_id=profile.id).first()
            if skill:
                db.session.delete(skill)
                db.session.commit()
                flash("Skill removed.", "info")
        return redirect(url_for("profile.skills"))

    return render_template("profile/skills.html", profile=profile)


# ─── Projects ────────────────────────────────────────────────────────────────
@profile_bp.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    user_id = request.current_user_id
    profile = _get_profile(user_id)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            proj = Project(
                profile_id=profile.id,
                title=sanitize_string(request.form.get("title", ""), 200),
                description=sanitize_text(request.form.get("description", ""), 2000),
                tech_stack=sanitize_string(request.form.get("tech_stack", ""), 500),
                github_url=sanitize_string(request.form.get("github_url", ""), 500),
                live_url=sanitize_string(request.form.get("live_url", ""), 500),
                start_date=sanitize_string(request.form.get("start_date", ""), 20),
                end_date=sanitize_string(request.form.get("end_date", ""), 20),
            )
            db.session.add(proj)
            db.session.commit()
            flash("Project added.", "success")
        elif action == "delete":
            pid = int(request.form.get("project_id", 0))
            proj = Project.query.filter_by(id=pid, profile_id=profile.id).first()
            if proj:
                db.session.delete(proj)
                db.session.commit()
                flash("Project removed.", "info")
        return redirect(url_for("profile.projects"))

    return render_template("profile/projects.html", profile=profile)


# ─── Experience ──────────────────────────────────────────────────────────────
@profile_bp.route("/experience", methods=["GET", "POST"])
@login_required
def experience():
    user_id = request.current_user_id
    profile = _get_profile(user_id)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            exp = Experience(
                profile_id=profile.id,
                company=sanitize_string(request.form.get("company", ""), 200),
                role=sanitize_string(request.form.get("role", ""), 200),
                start_date=sanitize_string(request.form.get("start_date", ""), 20),
                end_date=sanitize_string(request.form.get("end_date", ""), 20),
                is_current=bool(request.form.get("is_current")),
                description=sanitize_text(request.form.get("description", ""), 2000),
                location=sanitize_string(request.form.get("location", ""), 200),
            )
            db.session.add(exp)
            db.session.commit()
            flash("Experience entry added.", "success")
        elif action == "delete":
            eid = int(request.form.get("exp_id", 0))
            exp = Experience.query.filter_by(id=eid, profile_id=profile.id).first()
            if exp:
                db.session.delete(exp)
                db.session.commit()
                flash("Experience removed.", "info")
        return redirect(url_for("profile.experience"))

    return render_template("profile/experience.html", profile=profile)


# ─── Certifications ──────────────────────────────────────────────────────────
@profile_bp.route("/certifications", methods=["GET", "POST"])
@login_required
def certifications():
    user_id = request.current_user_id
    profile = _get_profile(user_id)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            cert = Certification(
                profile_id=profile.id,
                name=sanitize_string(request.form.get("name", ""), 200),
                issuing_org=sanitize_string(request.form.get("issuing_org", ""), 200),
                issue_date=sanitize_string(request.form.get("issue_date", ""), 20),
                expiry_date=sanitize_string(request.form.get("expiry_date", ""), 20),
                credential_id=sanitize_string(request.form.get("credential_id", ""), 200),
                credential_url=sanitize_string(request.form.get("credential_url", ""), 500),
            )
            db.session.add(cert)
            db.session.commit()
            flash("Certification added.", "success")
        elif action == "delete":
            cid = int(request.form.get("cert_id", 0))
            cert = Certification.query.filter_by(id=cid, profile_id=profile.id).first()
            if cert:
                db.session.delete(cert)
                db.session.commit()
                flash("Certification removed.", "info")
        return redirect(url_for("profile.certifications"))

    return render_template("profile/certifications.html", profile=profile)


def _safe_int(val) -> int | None:
    try:
        return int(val) if val else None
    except (ValueError, TypeError):
        return None
