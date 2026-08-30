"""
Resume Parser route – Upload PDF/DOCX and extract skills.
"""
import os
from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename
from app.utils.jwt_helper import login_required
from app.utils.validators import allowed_file
from app.ai.resume_parser import parse_resume_pdf, parse_resume_docx, extract_contact_info
from app.ai.skill_extractor import extract_skills_spacy
from app.ml.ats_scorer import predict_ats_score, classify_resume

parser_bp = Blueprint("parser", __name__)


@parser_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    result = None
    if request.method == "POST":
        f = request.files.get("resume_file")
        if not f or not f.filename:
            flash("Please select a file.", "warning")
            return render_template("resume/upload_parse.html", result=None)

        ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
        if ext not in {"pdf", "docx"}:
            flash("Only PDF and DOCX files are supported.", "danger")
            return render_template("resume/upload_parse.html", result=None)

        file_bytes = f.read()
        if ext == "pdf":
            text = parse_resume_pdf(file_bytes)
        else:
            text = parse_resume_docx(file_bytes)

        contact = extract_contact_info(text)
        skills = extract_skills_spacy(text)
        ats = predict_ats_score(text)
        category = classify_resume(text)

        result = {
            "text": text[:2000] + ("..." if len(text) > 2000 else ""),
            "contact": contact,
            "skills": skills,
            "ats": ats,
            "category": category,
            "filename": f.filename,
        }

    return render_template("resume/upload_parse.html", result=result)
