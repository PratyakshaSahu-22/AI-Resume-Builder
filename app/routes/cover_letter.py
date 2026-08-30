"""
Cover Letter Builder routes.
"""
import json
from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for
)
from app import db
from app.models import CoverLetter, User
from app.utils.jwt_helper import login_required
from app.utils.validators import sanitize_string, sanitize_text
from app.ai.text_generator import generate_cover_letter

cover_letter_bp = Blueprint("cover_letter", __name__)


@cover_letter_bp.route("/")
@login_required
def index():
    user_id = request.current_user_id
    letters = CoverLetter.query.filter_by(user_id=user_id).order_by(CoverLetter.updated_at.desc()).all()
    return render_template("cover_letter/index.html", letters=letters)


@cover_letter_bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    user_id = request.current_user_id
    user = User.query.get_or_404(user_id)
    profile = user.profile

    if not profile:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("profile.index"))

    if request.method == "POST":
        company = sanitize_string(request.form.get("company_name", ""), 200)
        job_role = sanitize_string(request.form.get("job_role", ""), 200)

        if not company or not job_role:
            flash("Company name and job role are required.", "danger")
            return render_template("cover_letter/generate.html", profile=profile)

        # Build profile_data for generator
        profile_data = {
            "full_name": profile.full_name,
            "skills": [s.name for s in profile.skills],
            "education": [e.to_dict() for e in profile.education],
            "experience": [x.to_dict() for x in profile.experience],
            "projects": [p.to_dict() for p in profile.projects],
        }

        content = generate_cover_letter(profile_data, company, job_role)

        letter = CoverLetter(
            user_id=user_id,
            company_name=company,
            job_role=job_role,
            content=content,
        )
        db.session.add(letter)
        db.session.commit()

        flash("Cover letter generated!", "success")
        return redirect(url_for("cover_letter.edit", letter_id=letter.id))

    return render_template("cover_letter/generate.html", profile=profile)


@cover_letter_bp.route("/<int:letter_id>/edit", methods=["GET", "POST"])
@login_required
def edit(letter_id: int):
    user_id = request.current_user_id
    letter = CoverLetter.query.filter_by(id=letter_id, user_id=user_id).first_or_404()

    if request.method == "POST":
        letter.company_name = sanitize_string(request.form.get("company_name", letter.company_name), 200)
        letter.job_role = sanitize_string(request.form.get("job_role", letter.job_role), 200)
        letter.content = sanitize_text(request.form.get("content", letter.content), 10000)
        db.session.commit()
        flash("Cover letter saved.", "success")
        return redirect(url_for("cover_letter.edit", letter_id=letter.id))

    return render_template("cover_letter/edit.html", letter=letter)


@cover_letter_bp.route("/<int:letter_id>/delete", methods=["POST"])
@login_required
def delete(letter_id: int):
    user_id = request.current_user_id
    letter = CoverLetter.query.filter_by(id=letter_id, user_id=user_id).first_or_404()
    db.session.delete(letter)
    db.session.commit()
    flash("Cover letter deleted.", "info")
    return redirect(url_for("cover_letter.index"))
