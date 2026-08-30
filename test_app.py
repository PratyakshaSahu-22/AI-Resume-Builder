"""
Functional test suite for AI Resume & Portfolio Builder.
Tests authentication, profile CRUD, AI/ML modules, and all routes.
Run: python test_app.py
"""
import sys
import os
import warnings
import json
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(__file__))

# Setup
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")

from app import create_app, db
app = create_app("testing")

results = []


def check(label, expr, expected=True):
    ok = bool(expr) == bool(expected)
    status = "[PASS]" if ok else "[FAIL]"
    print(f"  {status}  {label}")
    results.append((label, ok))
    return ok


def section(title):
    print(f"\n{'-'*55}")
    print(f"  {title}")
    print(f"{'-'*55}")


# ===========================================================================
# 1. Validators
# ===========================================================================
section("1. Validators")
from app.utils.validators import is_valid_email, is_strong_password, sanitize_string, sanitize_text

check("Valid email accepted", is_valid_email("user@example.com"))
check("Invalid email rejected", is_valid_email("not-an-email"), False)
valid, _ = is_strong_password("Secure123")
check("Strong password accepted", valid)
weak, _ = is_strong_password("weak")
check("Weak password rejected", not weak)
check("sanitize_string escapes HTML", "<" not in sanitize_string("<script>alert(1)</script>"))
check("sanitize_string truncates at max_length", len(sanitize_string("a" * 600, max_length=500)) == 500)


# ===========================================================================
# 2. Auth Service
# ===========================================================================
section("2. Auth Service (bcrypt)")
from app.services.auth_service import hash_password, check_password

hashed = hash_password("MyPassword1")
check("Password hashes to bcrypt string", hashed.startswith("$2b$"))
check("Correct password verifies", check_password("MyPassword1", hashed))
check("Wrong password is rejected", not check_password("WrongPass1", hashed))


# ===========================================================================
# 3. JWT Helpers
# ===========================================================================
section("3. JWT Helpers")
with app.app_context():
    from app.utils.jwt_helper import create_token, decode_token

    token = create_token(42, "testuser")
    check("Token is a non-empty string", isinstance(token, str) and len(token) > 20)
    payload = decode_token(token)
    check("Token sub == user_id", payload["sub"] == 42)
    check("Token username field correct", payload["username"] == "testuser")

    # Tampered token should raise
    try:
        decode_token(token[:-5] + "XXXXX")
        check("Tampered token rejected", False)
    except Exception:
        check("Tampered token rejected", True)


# ===========================================================================
# 4. AI - Skill Extraction
# ===========================================================================
section("4. AI - Skill Extraction (spaCy fallback)")
from app.ai.skill_extractor import extract_skills_spacy

sample = "Experienced in Python, Flask, React, Docker, machine learning and deep learning. Good communication skills."
skills = extract_skills_spacy(sample)
check("Technical skills list is non-empty", len(skills["technical"]) > 0)
check("Python detected", any("Python" in s for s in skills["technical"]))
check("Machine Learning detected", any("Machine Learning" in s for s in skills["technical"]))
check("Soft skills detected", len(skills["soft"]) > 0)


# ===========================================================================
# 5. AI - Text Generator
# ===========================================================================
section("5. AI - Text Generator (NLG)")
from app.ai.text_generator import generate_professional_summary, enhance_project_description, generate_cover_letter

profile_data = {
    "full_name": "Priya Sharma",
    "skills": ["Python", "Flask", "Machine Learning", "SQL"],
    "education": [{"degree": "BCA", "field_of_study": "Computer Science",
                   "institution": "Mumbai University", "start_year": 2021,
                   "end_year": 2024, "grade": "8.5", "description": ""}],
    "experience": [{"role": "ML Intern", "company": "TechCorp",
                    "start_date": "Jan 2024", "end_date": "Mar 2024",
                    "is_current": False, "description": "Built NLP models.",
                    "location": "Remote"}],
    "projects": [{"title": "AI Chatbot", "description": "A chatbot using NLP.",
                  "tech_stack": "Python, NLTK", "github_url": "", "live_url": "",
                  "start_date": "", "end_date": "", "ai_enhanced_description": ""}],
}

summary = generate_professional_summary(profile_data)
check("Summary is non-empty (>50 chars)", len(summary) > 50)
check("Summary references a known skill", any(s.lower() in summary.lower() for s in ["python", "flask", "machine learning"]))

enhanced = enhance_project_description("AI Chatbot", "A chatbot using NLP", "Python, NLTK, Flask")
check("Enhanced description is longer than 50 chars", len(enhanced) > 50)
check("Action verb present in enhanced description",
      any(v in enhanced for v in ["Designed", "Developed", "Built", "Implemented", "Engineered",
                                   "Created", "Optimized", "Deployed", "Integrated", "Automated",
                                   "Streamlined", "Enhanced", "Configured", "Managed", "Architected"]))

letter = generate_cover_letter(profile_data, "Google", "ML Engineer")
check("Cover letter is >200 chars", len(letter) > 200)
check("Company name appears in letter", "Google" in letter)
check("Job role appears in letter", "ML Engineer" in letter)
check("Candidate name appears in letter", "Priya Sharma" in letter)


# ===========================================================================
# 6. AI - Resume Parser (contact extraction)
# ===========================================================================
section("6. AI - Resume Parser (contact info extraction)")
from app.ai.resume_parser import extract_contact_info

text = "John Doe\nEmail: john@example.com\nPhone: +91 9876543210\nExperience in Python."
contact = extract_contact_info(text)
check("Email extracted from resume text", contact["email"] == "john@example.com")
check("Phone extracted from resume text", contact["phone"] is not None)


# ===========================================================================
# 7. ML - ATS Scorer, JD Matching, Classification
# ===========================================================================
section("7. ML - ATS Scorer, JD Matching, Classification")
from app.ml.ats_scorer import (
    predict_ats_score, match_resume_to_jd,
    generate_improvement_suggestions, classify_resume
)

full_resume = (
    "SUMMARY\nExperienced Python developer with expertise in machine learning and web development.\n\n"
    "SKILLS\nPython, Flask, React, SQL, Machine Learning, TensorFlow, Docker\n\n"
    "EDUCATION\nB.Tech Computer Science - IIT Delhi 2020-2024 CGPA: 8.5\n\n"
    "EXPERIENCE\nSoftware Engineer at TechCorp Bangalore Jan 2023 - Present\n"
    "Built REST APIs and deployed ML models using Flask and Docker.\n\n"
    "PROJECTS\nAI Resume Builder - Python, Flask, NLP, scikit-learn\n"
    "Developed an ATS-friendly resume generation tool using NLP and machine learning.\n\n"
    "CERTIFICATIONS\nAWS Solutions Architect - Amazon Web Services 2023\n\n"
    "Email: john@example.com\nLinkedIn: linkedin.com/in/john\nGitHub: github.com/john\n"
)
jd = "Looking for a Python developer with Flask, machine learning, and SQL experience."

ats = predict_ats_score(full_resume, jd)
check("ATS score is a float", isinstance(ats["ats_score"], float))
check("ATS score is in range 0-100", 0 <= ats["ats_score"] <= 100)
check("ATS score > 50 for a complete resume", ats["ats_score"] > 50)
check("Word count returned", ats["word_count"] > 0)
check("Matched sections returned", len(ats["matched_sections"]) > 0)

match = match_resume_to_jd(full_resume, jd)
check("Match score is a float", isinstance(match["match_score"], float))
check("Match score is in range 0-100", 0 <= match["match_score"] <= 100)
check("Method reported in match result", "method" in match)

suggestions = generate_improvement_suggestions(full_resume, ats)
check("Suggestions returned as list", isinstance(suggestions, list))

cat = classify_resume(full_resume)
check("Resume classified to a category", isinstance(cat, str) and len(cat) > 0)
check("Category is a known type", any(k in cat for k in ["Software", "Web", "AI", "Data", "DevOps", "General"]))


# ===========================================================================
# 8. Database ORM - User, Profile, CRUD
# ===========================================================================
section("8. Database ORM - User + Profile + CRUD")
with app.app_context():
    db.create_all()
    from app.models import (
        User, Profile, Skill, Education, Project,
        Experience, Certification, Resume, CoverLetter, Portfolio
    )

    # Remove any leftover test data
    test_email = "test_functional@example.com"
    existing = User.query.filter_by(email=test_email).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    # Create user + profile
    user = User(
        username="test_user_func",
        email=test_email,
        password_hash=hash_password("Test1234"),
    )
    db.session.add(user)
    db.session.flush()

    profile = Profile(
        user_id=user.id, full_name="Test User",
        phone="+91 9876543210", location="Mumbai",
        summary="",   # intentionally empty so AI generates it
    )
    db.session.add(profile)
    db.session.flush()

    for obj in [
        Skill(profile_id=profile.id, name="Python", category="Programming", proficiency="Expert"),
        Education(profile_id=profile.id, institution="Test Uni", degree="BCA",
                  field_of_study="CS", start_year=2021, end_year=2024, grade="8.0"),
        Project(profile_id=profile.id, title="Test Project",
                description="A test project.", tech_stack="Python, Flask"),
        Experience(profile_id=profile.id, company="TestCo", role="Intern",
                   start_date="Jan 2023", end_date="Mar 2023"),
        Certification(profile_id=profile.id, name="AWS Cert", issuing_org="Amazon"),
    ]:
        db.session.add(obj)

    db.session.commit()

    u = User.query.filter_by(email=test_email).first()
    check("User saved", u is not None)
    check("Profile linked to user", u.profile is not None)
    check("Skill saved", len(u.profile.skills) == 1)
    check("Education saved", len(u.profile.education) == 1)
    check("Project saved", len(u.profile.projects) == 1)
    check("Experience saved", len(u.profile.experience) == 1)
    check("Certification saved", len(u.profile.certifications) == 1)


# ===========================================================================
# 9. Resume Service - Full AI Pipeline
# ===========================================================================
section("9. Resume Service - Full AI Pipeline")
with app.app_context():
    from app.models import User
    from app.services.resume_service import build_resume_content, analyse_resume
    from app.routes.resume import _dict_to_plaintext

    user = User.query.filter_by(email="test_functional@example.com").first()
    content = build_resume_content(user.profile)
    check("Resume content dict returned", isinstance(content, dict))
    check("AI summary generated (>20 chars)", len(content.get("summary", "")) > 20)
    check("Skills included", len(content.get("skills", [])) > 0)
    check("Education included", len(content.get("education", [])) > 0)
    check("Projects included", len(content.get("projects", [])) > 0)

    resume_text = _dict_to_plaintext(content)
    check("Plain text built (>50 chars)", len(resume_text) > 50)

    analysis = analyse_resume(resume_text, "Python Flask developer")
    check("ATS analysis returned", "ats" in analysis)
    check("Suggestions list returned", isinstance(analysis.get("suggestions"), list))
    check("JD match score returned", "match" in analysis)
    check("Category classification returned", "category" in analysis)


# ===========================================================================
# 10. HTTP Routes - Unauthenticated
# ===========================================================================
section("10. HTTP Routes - Unauthenticated")
with app.test_client() as client:
    r = client.get("/")
    check("GET /  -> 200 Landing page", r.status_code == 200)
    check("Landing page contains 'Resume'", b"Resume" in r.data)

    r = client.get("/auth/login")
    check("GET /auth/login -> 200", r.status_code == 200)

    r = client.get("/auth/signup")
    check("GET /auth/signup -> 200", r.status_code == 200)

    r = client.get("/dashboard/", follow_redirects=False)
    check("GET /dashboard/ without auth -> 302 redirect", r.status_code == 302)

    r = client.get("/profile/", follow_redirects=False)
    check("GET /profile/ without auth -> 302 redirect", r.status_code == 302)

    r = client.get("/resume/", follow_redirects=False)
    check("GET /resume/ without auth -> 302 redirect", r.status_code == 302)

    r = client.get("/nonexistent-xyz-page")
    check("GET /nonexistent -> 404", r.status_code == 404)


# ===========================================================================
# 11. HTTP Routes - Authenticated
# ===========================================================================
section("11. HTTP Routes - Authenticated Session")
with app.test_client() as client:
    with app.app_context():
        from app.utils.jwt_helper import create_token
        from app.models import User
        user = User.query.filter_by(email="test_functional@example.com").first()
        token = create_token(user.id, user.username)
        uid = user.id
        uname = user.username

    with client.session_transaction() as sess:
        sess["jwt_token"] = token
        sess["user_id"] = uid
        sess["username"] = uname

    pages = [
        ("/dashboard/", "Dashboard 200"),
        ("/profile/", "Profile personal 200"),
        ("/profile/education", "Profile education 200"),
        ("/profile/skills", "Profile skills 200"),
        ("/profile/projects", "Profile projects 200"),
        ("/profile/experience", "Profile experience 200"),
        ("/profile/certifications", "Profile certifications 200"),
        ("/resume/", "Resume index 200"),
        ("/resume/generate", "Resume generate form 200"),
        ("/cover-letter/", "Cover letter index 200"),
        ("/cover-letter/generate", "Cover letter generate form 200"),
        ("/portfolio/", "Portfolio index 200"),
        ("/portfolio/generate", "Portfolio generate form 200"),
        ("/parser/upload", "Resume parser upload page 200"),
    ]
    for url, label in pages:
        r = client.get(url)
        check(label, r.status_code == 200)


# ===========================================================================
# Cleanup + Summary
# ===========================================================================
with app.app_context():
    from app.models import User
    u = User.query.filter_by(email="test_functional@example.com").first()
    if u:
        db.session.delete(u)
        db.session.commit()

total = len(results)
passed = sum(1 for _, ok in results if ok)
failed = total - passed

print(f"\n{'='*55}")
print(f"  RESULTS: {passed}/{total} passed   {failed} failed")
print(f"{'='*55}\n")

if failed > 0:
    print("  Failed tests:")
    for label, ok in results:
        if not ok:
            print(f"    [FAIL]  {label}")
    print()
    sys.exit(1)
else:
    print("  All tests passed! Application is ready to run.")
    print(f"  Start the server with:  python run.py")
    print()
