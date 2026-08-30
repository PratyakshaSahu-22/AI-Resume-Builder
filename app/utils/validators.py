"""
Input validation helpers – sanitise and validate user-submitted data.
"""
import re
import html


def sanitize_string(value: str, max_length: int = 500) -> str:
    """Strip HTML tags and truncate."""
    if not isinstance(value, str):
        return ""
    clean = html.escape(value.strip())
    return clean[:max_length]


def sanitize_text(value: str, max_length: int = 5000) -> str:
    """Sanitise multi-line text areas."""
    if not isinstance(value, str):
        return ""
    clean = html.escape(value.strip())
    return clean[:max_length]


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-z]{2,}$"
    return bool(re.match(pattern, email, re.IGNORECASE))


def is_valid_url(url: str) -> bool:
    if not url:
        return True  # optional field
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url, re.IGNORECASE))


def is_strong_password(password: str) -> tuple[bool, str]:
    """Return (valid, message)."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    return True, "OK"


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
