"""
Dashboard route.
"""
from flask import Blueprint, render_template, request
from app.models import User, Resume, CoverLetter, Portfolio
from app.utils.jwt_helper import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    user_id = request.current_user_id
    user = User.query.get_or_404(user_id)
    profile = user.profile

    resume_count = Resume.query.filter_by(user_id=user_id).count()
    cl_count = CoverLetter.query.filter_by(user_id=user_id).count()
    portfolio_count = Portfolio.query.filter_by(user_id=user_id).count()

    # Latest resume for ATS score display
    latest_resume = (
        Resume.query
        .filter_by(user_id=user_id)
        .order_by(Resume.updated_at.desc())
        .first()
    )

    return render_template(
        "dashboard/index.html",
        user=user,
        profile=profile,
        resume_count=resume_count,
        cl_count=cl_count,
        portfolio_count=portfolio_count,
        latest_resume=latest_resume,
    )
