"""
Authentication routes – Signup, Login, Logout.
"""
from flask import (
    Blueprint, flash, redirect, render_template,
    request, session, url_for, current_app
)
from app import db, limiter
from app.models import User, Profile
from app.services.auth_service import hash_password, check_password
from app.utils.jwt_helper import create_token
from app.utils.validators import is_valid_email, is_strong_password, sanitize_string

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def signup():
    if session.get("jwt_token"):
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = sanitize_string(request.form.get("username", ""), 80)
        email = sanitize_string(request.form.get("email", ""), 120).lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        valid_pw, pw_msg = is_strong_password(password)
        if not valid_pw:
            errors.append(pw_msg)
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")
        if User.query.filter_by(username=username).first():
            errors.append("This username is already taken.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("auth/signup.html", username=username, email=email)

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        db.session.add(user)
        db.session.flush()  # get user.id

        # Create blank profile
        profile = Profile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        current_app.logger.info(f"New user registered: {email}")
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per hour")
def login():
    if session.get("jwt_token"):
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = sanitize_string(request.form.get("email", ""), 120).lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not check_password(password, user.password_hash):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", email=email)

        # Issue JWT and store in session
        token = create_token(user.id, user.username)
        session["jwt_token"] = token
        session["user_id"] = user.id
        session["username"] = user.username
        session.permanent = True

        current_app.logger.info(f"User logged in: {email}")
        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
