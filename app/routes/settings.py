"""
Account Settings route – change username, email, password.
"""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app import db
from app.models import User
from app.services.auth_service import hash_password, check_password
from app.utils.jwt_helper import login_required, create_token
from app.utils.validators import sanitize_string, is_valid_email, is_strong_password

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = request.current_user_id
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        action = request.form.get("action")

        # ── Change Username ──────────────────────────────────────────────────
        if action == "change_username":
            new_username = sanitize_string(request.form.get("username", "").strip(), 80)
            if not new_username or len(new_username) < 3:
                flash("Username must be at least 3 characters.", "danger")
            elif User.query.filter(User.username == new_username, User.id != user_id).first():
                flash("That username is already taken. Please choose another.", "danger")
            else:
                user.username = new_username
                db.session.commit()
                # Refresh session and token with new username
                session["username"] = new_username
                token = create_token(user.id, new_username)
                session["jwt_token"] = token
                flash(f'Username updated to "{new_username}" successfully!', "success")
            return redirect(url_for("settings.index"))

        # ── Change Email ─────────────────────────────────────────────────────
        elif action == "change_email":
            new_email = sanitize_string(request.form.get("email", "").strip().lower(), 120)
            if not is_valid_email(new_email):
                flash("Please enter a valid email address.", "danger")
            elif User.query.filter(User.email == new_email, User.id != user_id).first():
                flash("That email is already registered to another account.", "danger")
            else:
                user.email = new_email
                db.session.commit()
                flash(f'Email updated to "{new_email}" successfully!', "success")
            return redirect(url_for("settings.index"))

        # ── Change Password ──────────────────────────────────────────────────
        elif action == "change_password":
            current_pw = request.form.get("current_password", "")
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")

            if not check_password(current_pw, user.password_hash):
                flash("Current password is incorrect.", "danger")
            elif new_pw != confirm_pw:
                flash("New passwords do not match.", "danger")
            else:
                valid, msg = is_strong_password(new_pw)
                if not valid:
                    flash(msg, "danger")
                else:
                    user.password_hash = hash_password(new_pw)
                    db.session.commit()
                    flash("Password changed successfully!", "success")
            return redirect(url_for("settings.index"))

    return render_template("auth/settings.html", user=user)


@settings_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    """Permanently delete user account and all associated data."""
    user_id = request.current_user_id
    user = User.query.get_or_404(user_id)

    confirm = request.form.get("confirm_delete", "").strip()
    if confirm != user.username:
        flash("Confirmation did not match. Account was NOT deleted.", "danger")
        return redirect(url_for("settings.index"))

    # SQLAlchemy cascade="all, delete-orphan" on relationships handles
    # Profile → Education, Skills, Projects, Experience, Certifications
    # Resumes, CoverLetters, Portfolios are also cascaded from User
    db.session.delete(user)
    db.session.commit()

    # Clear the session
    session.clear()
    flash("Your account and all data have been permanently deleted.", "info")
    return redirect(url_for("main.index"))
