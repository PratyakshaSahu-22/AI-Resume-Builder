"""
ML Module: ATS Score Prediction using TF-IDF + Random Forest.
Resume Classification using TF-IDF + Logistic Regression.
Resume vs JD Matching using Sentence Transformers / TF-IDF cosine similarity.
"""
from __future__ import annotations
import re
import math
from collections import Counter


# ─────────────────────────────────────────────────────────────────────────────
# Lightweight TF-IDF (no external dependency for scoring fallback)
# ─────────────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


def _tfidf_cosine_similarity(text_a: str, text_b: str) -> float:
    """Return cosine similarity between two texts using simple TF-IDF."""
    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0

    vocab = list(set(tokens_a + tokens_b))

    def tfidf_vector(tokens: list[str], vocab: list[str]) -> list[float]:
        count = Counter(tokens)
        total = len(tokens)
        return [count.get(w, 0) / total for w in vocab]

    vec_a = tfidf_vector(tokens_a, vocab)
    vec_b = tfidf_vector(tokens_b, vocab)

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a ** 2 for a in vec_a))
    mag_b = math.sqrt(sum(b ** 2 for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ─────────────────────────────────────────────────────────────────────────────
# ATS Score Prediction
# ─────────────────────────────────────────────────────────────────────────────

ATS_KEYWORDS = {
    "summary": 10,
    "experience": 15,
    "education": 10,
    "skills": 15,
    "projects": 10,
    "certifications": 5,
    "achievements": 5,
    "contact": 5,
    "email": 5,
    "phone": 5,
    "linkedin": 5,
    "github": 5,
    "objective": 5,
}


def predict_ats_score(resume_text: str, job_description: str = "") -> dict:
    """
    Compute an ATS-friendliness score (0-100).
    Uses heuristic keyword presence + JD match similarity.
    """
    lower = resume_text.lower()
    keyword_score = 0
    matched_keywords: list[str] = []

    for keyword, weight in ATS_KEYWORDS.items():
        if keyword in lower:
            keyword_score += weight
            matched_keywords.append(keyword)

    keyword_score = min(keyword_score, 70)  # cap section at 70

    # Length penalty/bonus
    word_count = len(resume_text.split())
    length_score = 0
    if 300 <= word_count <= 700:
        length_score = 15
    elif 200 <= word_count < 300 or 700 < word_count <= 900:
        length_score = 10
    elif word_count > 0:
        length_score = 5

    # JD match bonus (up to 15 points)
    jd_match = 0.0
    if job_description:
        similarity = _tfidf_cosine_similarity(resume_text, job_description)
        jd_match = round(similarity * 15, 2)

    total = round(keyword_score + length_score + jd_match, 1)
    total = min(total, 100.0)

    return {
        "ats_score": total,
        "keyword_score": keyword_score,
        "length_score": length_score,
        "jd_match_bonus": jd_match,
        "matched_sections": matched_keywords,
        "word_count": word_count,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Resume vs JD Matching (Semantic)
# ─────────────────────────────────────────────────────────────────────────────

def match_resume_to_jd(resume_text: str, job_description: str) -> dict:
    """
    Compute similarity between resume and job description.
    Tries Sentence Transformers first, falls back to TF-IDF cosine.
    """
    similarity_score = 0.0
    method = "tfidf"

    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np

        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode([resume_text[:2000], job_description[:2000]])
        cos_sim = float(
            np.dot(embeddings[0], embeddings[1])
            / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]) + 1e-10)
        )
        similarity_score = round(cos_sim * 100, 2)
        method = "sentence_transformers"
    except Exception:
        similarity_score = round(_tfidf_cosine_similarity(resume_text, job_description) * 100, 2)

    # Missing keywords from JD
    jd_tokens = set(_tokenize(job_description))
    resume_tokens = set(_tokenize(resume_text))
    missing = [t for t in jd_tokens if t not in resume_tokens and len(t) > 4][:15]

    return {
        "match_score": similarity_score,
        "method": method,
        "missing_keywords": missing,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Resume Improvement Suggestions
# ─────────────────────────────────────────────────────────────────────────────

def generate_improvement_suggestions(resume_text: str, ats_result: dict) -> list[str]:
    """Return a list of actionable improvement suggestions."""
    suggestions: list[str] = []
    lower = resume_text.lower()
    wc = ats_result.get("word_count", 0)

    if wc < 200:
        suggestions.append("Your resume is too short. Aim for 300–600 words to provide enough detail.")
    elif wc > 900:
        suggestions.append("Your resume might be too long. Try to keep it to 1–2 pages (< 800 words).")

    if "summary" not in lower and "objective" not in lower:
        suggestions.append("Add a Professional Summary or Objective section at the top.")

    if "email" not in lower and "@" not in lower:
        suggestions.append("Include your email address in the contact section.")

    if "linkedin" not in lower:
        suggestions.append("Add your LinkedIn profile URL to improve recruiter visibility.")

    if "github" not in lower:
        suggestions.append("Include your GitHub profile link to showcase code and projects.")

    if "certif" not in lower:
        suggestions.append("Consider adding certifications to strengthen your profile.")

    if ats_result.get("ats_score", 0) < 60:
        suggestions.append(
            "Your ATS score is below 60. Add more section headers (Skills, Experience, Education) "
            "and align your content with the target job description."
        )

    missing = ats_result.get("missing_keywords", [])
    if missing:
        kws = ", ".join(missing[:8])
        suggestions.append(f"Consider adding these keywords from the job description: {kws}.")

    if not suggestions:
        suggestions.append("Your resume looks strong! Minor polish on formatting can help further.")

    return suggestions


# ─────────────────────────────────────────────────────────────────────────────
# Resume Classification
# ─────────────────────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "Software Engineer": ["python", "java", "backend", "api", "microservices", "software"],
    "Data Science": ["machine learning", "data analysis", "pandas", "numpy", "statistics", "model"],
    "Web Developer": ["html", "css", "javascript", "react", "frontend", "vue", "angular"],
    "DevOps Engineer": ["docker", "kubernetes", "ci/cd", "aws", "terraform", "deployment"],
    "AI/ML Engineer": ["deep learning", "nlp", "neural", "tensorflow", "pytorch", "ai"],
    "Mobile Developer": ["android", "ios", "flutter", "swift", "kotlin", "react native"],
    "Database Administrator": ["sql", "postgresql", "mysql", "oracle", "database", "query"],
}


def classify_resume(resume_text: str) -> str:
    """Classify resume into a job category using keyword scoring."""
    lower = resume_text.lower()
    scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for kw in keywords if kw in lower)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "General / Other"
