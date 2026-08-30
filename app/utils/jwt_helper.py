"""
JWT utility helpers – token creation and verification without flask-jwt-extended.
Uses PyJWT directly for lightweight authentication.
"""
import datetime
import functools

import jwt
from flask import current_app, jsonify, request, session


def create_token(user_id: int, username: str) -> str:
    """Return a signed JWT access token."""
    payload = {
        "sub": str(user_id),          # PyJWT >= 2.x requires sub to be a string
        "username": username,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"],
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError."""
    payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    # Cast sub back to int for use as user_id
    payload["sub"] = int(payload["sub"])
    return payload


def get_token_from_request() -> str | None:
    """Extract JWT from cookie or Authorization header."""
    # Prefer session cookie
    token = session.get("jwt_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
    return token


def login_required(f):
    """Decorator that protects a route – redirects to login if not authenticated."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import redirect, url_for, flash
        token = get_token_from_request()
        if not token:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        try:
            payload = decode_token(token)
            request.current_user_id = payload["sub"]
            request.current_username = payload["username"]
        except jwt.ExpiredSignatureError:
            session.pop("jwt_token", None)
            flash("Session expired. Please log in again.", "warning")
            return redirect(url_for("auth.login"))
        except jwt.InvalidTokenError:
            session.pop("jwt_token", None)
            flash("Invalid session. Please log in.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def api_login_required(f):
    """Decorator for JSON API endpoints."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        try:
            payload = decode_token(token)
            request.current_user_id = payload["sub"]
            request.current_username = payload["username"]
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            return jsonify({"error": str(e)}), 401
        return f(*args, **kwargs)
    return decorated
