"""
Portfolio Builder routes.
"""
import json
from flask import (
    Blueprint, flash, redirect, render_template,
    request, url_for
)
from app import db
from app.models import Portfolio, User
from app.utils.jwt_helper import login_required
from app.utils.validators import sanitize_text
from app.services.portfolio_service import build_portfolio_content

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/")
@login_required
def index():
    user_id = request.current_user_id
    portfolios = Portfolio.query.filter_by(user_id=user_id).order_by(Portfolio.updated_at.desc()).all()
    return render_template("portfolio/index.html", portfolios=portfolios)


@portfolio_bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    user_id = request.current_user_id
    user = User.query.get_or_404(user_id)
    profile = user.profile

    if not profile:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("profile.index"))

    if request.method == "POST":
        content = build_portfolio_content(profile)

        portfolio = Portfolio(
            user_id=user_id,
            about=content["about"],
            skills_section=json.dumps(content["skills"]),
            projects_section=json.dumps(content["projects"]),
            experience_section=json.dumps(content["experience"]),
            contact_section=json.dumps(content["contact"]),
        )
        db.session.add(portfolio)
        db.session.commit()

        flash("Portfolio generated!", "success")
        return redirect(url_for("portfolio.edit", portfolio_id=portfolio.id))

    return render_template("portfolio/generate.html", profile=profile)


@portfolio_bp.route("/<int:portfolio_id>/edit", methods=["GET", "POST"])
@login_required
def edit(portfolio_id: int):
    user_id = request.current_user_id
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id).first_or_404()

    if request.method == "POST":
        portfolio.about = sanitize_text(request.form.get("about", portfolio.about or ""), 5000)
        portfolio.is_published = bool(request.form.get("is_published"))
        db.session.commit()
        flash("Portfolio saved.", "success")
        return redirect(url_for("portfolio.edit", portfolio_id=portfolio.id))

    skills = json.loads(portfolio.skills_section or "{}")
    projects = json.loads(portfolio.projects_section or "[]")
    experience = json.loads(portfolio.experience_section or "[]")
    contact = json.loads(portfolio.contact_section or "{}")

    return render_template(
        "portfolio/edit.html",
        portfolio=portfolio,
        skills=skills,
        projects=projects,
        experience=experience,
        contact=contact,
    )


@portfolio_bp.route("/<int:portfolio_id>/view")
def view(portfolio_id: int):
    """Public portfolio view."""
    portfolio = Portfolio.query.filter_by(id=portfolio_id, is_published=True).first_or_404()
    user = User.query.get(portfolio.user_id)
    skills = json.loads(portfolio.skills_section or "{}")
    projects = json.loads(portfolio.projects_section or "[]")
    experience = json.loads(portfolio.experience_section or "[]")
    contact = json.loads(portfolio.contact_section or "{}")

    return render_template(
        "portfolio/view.html",
        portfolio=portfolio,
        user=user,
        skills=skills,
        projects=projects,
        experience=experience,
        contact=contact,
    )


@portfolio_bp.route("/<int:portfolio_id>/delete", methods=["POST"])
@login_required
def delete(portfolio_id: int):
    user_id = request.current_user_id
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id).first_or_404()
    db.session.delete(portfolio)
    db.session.commit()
    flash("Portfolio deleted.", "info")
    return redirect(url_for("portfolio.index"))
