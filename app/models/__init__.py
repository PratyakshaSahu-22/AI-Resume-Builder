"""
SQLAlchemy ORM Models
All tables with proper relationships and normalization.
"""
from datetime import datetime

from app import db


# ─────────────────────────────────────────────────────────────────────────────
# User
# ─────────────────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    resumes = db.relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    cover_letters = db.relationship("CoverLetter", back_populates="user", cascade="all, delete-orphan")
    portfolios = db.relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Profile
# ─────────────────────────────────────────────────────────────────────────────
class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    # Personal details
    full_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(200))
    linkedin = db.Column(db.String(300))
    github = db.Column(db.String(300))
    website = db.Column(db.String(300))
    summary = db.Column(db.Text)
    profile_picture = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="profile")
    education = db.relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    skills = db.relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    projects = db.relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    experience = db.relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    certifications = db.relationship("Certification", back_populates="profile", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone": self.phone,
            "location": self.location,
            "linkedin": self.linkedin,
            "github": self.github,
            "website": self.website,
            "summary": self.summary,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Education
# ─────────────────────────────────────────────────────────────────────────────
class Education(db.Model):
    __tablename__ = "education"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)

    institution = db.Column(db.String(200), nullable=False)
    degree = db.Column(db.String(200), nullable=False)
    field_of_study = db.Column(db.String(200))
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    grade = db.Column(db.String(50))
    description = db.Column(db.Text)

    profile = db.relationship("Profile", back_populates="education")

    def to_dict(self):
        return {
            "id": self.id,
            "institution": self.institution,
            "degree": self.degree,
            "field_of_study": self.field_of_study,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "grade": self.grade,
            "description": self.description,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Skill
# ─────────────────────────────────────────────────────────────────────────────
class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))          # e.g. "Programming", "Tools"
    proficiency = db.Column(db.String(50))        # Beginner / Intermediate / Expert

    profile = db.relationship("Profile", back_populates="skills")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "proficiency": self.proficiency,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Project
# ─────────────────────────────────────────────────────────────────────────────
class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    tech_stack = db.Column(db.String(500))        # comma-separated
    github_url = db.Column(db.String(500))
    live_url = db.Column(db.String(500))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    ai_enhanced_description = db.Column(db.Text)  # AI-improved version

    profile = db.relationship("Profile", back_populates="projects")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "tech_stack": self.tech_stack,
            "github_url": self.github_url,
            "live_url": self.live_url,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "ai_enhanced_description": self.ai_enhanced_description,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Experience
# ─────────────────────────────────────────────────────────────────────────────
class Experience(db.Model):
    __tablename__ = "experience"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)

    company = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))

    profile = db.relationship("Profile", back_populates="experience")

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "role": self.role,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "is_current": self.is_current,
            "description": self.description,
            "location": self.location,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Certification
# ─────────────────────────────────────────────────────────────────────────────
class Certification(db.Model):
    __tablename__ = "certifications"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profiles.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    issuing_org = db.Column(db.String(200))
    issue_date = db.Column(db.String(20))
    expiry_date = db.Column(db.String(20))
    credential_id = db.Column(db.String(200))
    credential_url = db.Column(db.String(500))

    profile = db.relationship("Profile", back_populates="certifications")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "issuing_org": self.issuing_org,
            "issue_date": self.issue_date,
            "expiry_date": self.expiry_date,
            "credential_id": self.credential_id,
            "credential_url": self.credential_url,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Resume
# ─────────────────────────────────────────────────────────────────────────────
class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), default="My Resume")
    content = db.Column(db.Text)           # JSON-serialised resume sections
    ats_score = db.Column(db.Float, default=0.0)
    job_description = db.Column(db.Text)   # JD used for matching
    match_score = db.Column(db.Float, default=0.0)
    suggestions = db.Column(db.Text)       # JSON list of NLP suggestions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="resumes")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "ats_score": self.ats_score,
            "match_score": self.match_score,
            "created_at": self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Cover Letter
# ─────────────────────────────────────────────────────────────────────────────
class CoverLetter(db.Model):
    __tablename__ = "cover_letters"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    company_name = db.Column(db.String(200))
    job_role = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="cover_letters")

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "job_role": self.job_role,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Portfolio
# ─────────────────────────────────────────────────────────────────────────────
class Portfolio(db.Model):
    __tablename__ = "portfolios"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    about = db.Column(db.Text)
    skills_section = db.Column(db.Text)    # JSON
    projects_section = db.Column(db.Text)  # JSON
    experience_section = db.Column(db.Text)
    contact_section = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="portfolios")

    def to_dict(self):
        return {
            "id": self.id,
            "about": self.about,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat(),
        }
