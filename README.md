# 🤖 AI Resume & Portfolio Builder

> **A full-stack AI/ML powered web application** that helps students generate ATS-friendly resumes, personalised cover letters, and digital portfolios using Machine Learning and NLP — built with Python, Flask, and Bootstrap 5.

<br/>

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-black?style=flat-square&logo=flask)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=flat-square&logo=bootstrap)
![SQLite](https://img.shields.io/badge/Database-SQLite%20%2F%20PostgreSQL-blue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [AI / ML Modules](#-ai--ml-modules)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Screenshots](#-screenshots)
- [Database Schema](#-database-schema)
- [Security](#-security-cia-triad)
- [API Routes](#-api-routes)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📖 About the Project

Many students struggle to present their skills and projects in an attractive, professional format. Generic resume templates do not highlight individual strengths.

**AI Resume & Portfolio Builder** solves this by using Machine Learning and NLP to:

- Automatically generate **ATS-friendly resumes** tailored to student profiles
- Predict **ATS scores (0–100)** and suggest improvements
- Match resumes against **job descriptions** using Sentence Transformers
- Generate **personalised cover letters** for specific companies and roles
- Build **shareable digital portfolios** with a public URL
- Extract skills from **uploaded PDF/DOCX resumes** using spaCy NER

This project is designed as a **Final Year BCA / B.Tech AI-ML Major Project** while remaining lightweight and fully functional.

---

## ✨ Features

### 🔐 Authentication
- Student Signup & Login
- JWT-based stateless authentication
- bcrypt password hashing
- CSRF protection on all forms
- Protected routes with session management
- Account Settings — change username, email, password
- **Delete Account** — permanently removes all user data

### 📊 Dashboard
- Resume count, cover letter count, portfolio count
- Latest ATS score with visual progress bar
- Profile completeness tracker
- Quick action cards for all modules

### 👤 Profile Module (Full CRUD)
| Section | Fields |
|---|---|
| Personal Details | Name, phone, location, LinkedIn, GitHub, website, summary, profile picture |
| Education | Institution, degree, field, years, grade |
| Skills | Name, category, proficiency level |
| Projects | Title, description, tech stack, GitHub, live URL |
| Experience | Role, company, dates, location, description |
| Certifications | Name, issuing org, dates, credential ID & URL |

### 📄 AI Resume Builder
- Generate ATS-friendly resume from profile in one click
- AI-enhanced project descriptions using action verbs
- AI-generated professional summary
- Real-time ATS Score (0–100) with progress bar
- JD Match Score using Sentence Transformers cosine similarity
- NLP-based improvement suggestions
- Full edit capability after generation
- Live preview with print support
- **Download as PDF** (WeasyPrint / xhtml2pdf)

### ✉️ AI Cover Letter Generator
- Enter company name + job role
- AI generates personalised, professional cover letter
- Uses your profile data (skills, education, experience, projects)
- Fully editable after generation

### 🌐 AI Portfolio Generator
- Generates about, skills, projects, experience, and contact sections
- Publish to get a shareable public URL
- Clean, responsive single-page portfolio design

### 📤 Resume Parser
- Upload existing PDF or DOCX resume
- Extracts text, contact info, skills, ATS score, and category
- Powered by pdfplumber, python-docx, and spaCy

---

## 🧠 AI / ML Modules

| Module | Technique | Library |
|---|---|---|
| Resume Parsing | PDF/DOCX text extraction + regex | pdfplumber, python-docx |
| Skill Extraction | spaCy NER noun chunks + keyword vocabulary | spaCy |
| Professional Summary | Template-based NLG with role detection | Python |
| Project Enhancement | Action verb injection + structured NLG | Python |
| Cover Letter NLG | Profile-aware personalised letter generation | Python |
| ATS Score Prediction | Keyword heuristics + TF-IDF length scoring | Python math |
| JD Match Analysis | Cosine similarity on sentence embeddings | Sentence Transformers |
| Resume Classification | Keyword scoring across 7 job categories | Python |
| Improvement Suggestions | Rule-based NLP feedback on resume gaps | Python + NLTK |

> All AI/ML modules are **local** — no external LLM API calls required. Sentence Transformers uses the lightweight `all-MiniLM-L6-v2` model.

---

## 🛠 Tech Stack

**Backend**
- Python 3.13
- Flask 3.1 (Application Factory pattern)
- SQLAlchemy ORM 2.0
- SQLite (development) / PostgreSQL (production)
- PyJWT 2.13 — JWT authentication
- bcrypt — password hashing
- Flask-WTF — CSRF protection
- Flask-Limiter — rate limiting

**Frontend**
- Bootstrap 5.3
- Bootstrap Icons
- Jinja2 templating
- Vanilla JavaScript

**AI / ML**
- spaCy 3.8 — NER and skill extraction
- Sentence Transformers — semantic JD matching
- pdfplumber — PDF parsing
- python-docx — DOCX parsing
- NLTK — NLP utilities

**PDF Generation**
- WeasyPrint (recommended)
- xhtml2pdf (fallback)

---

## 📁 Project Structure

```
ai_resume_builder/
│
├── run.py                          # Entry point
├── requirements.txt                # All dependencies
├── .env.example                    # Environment variable template
├── README.md
│
├── instance/
│   └── dev.db                      # SQLite database (auto-created)
│
├── logs/
│   └── app.log                     # Rotating application logs
│
└── app/
    ├── __init__.py                  # Flask app factory
    ├── config.py                    # Dev / Prod / Test configurations
    │
    ├── models/
    │   └── __init__.py              # All SQLAlchemy ORM models (10 tables)
    │
    ├── routes/                      # Flask Blueprints
    │   ├── main.py                  # Landing page
    │   ├── auth.py                  # Signup, Login, Logout
    │   ├── dashboard.py             # Dashboard
    │   ├── profile.py               # Profile CRUD
    │   ├── resume.py                # Resume Builder
    │   ├── cover_letter.py          # Cover Letter Builder
    │   ├── portfolio.py             # Portfolio Builder
    │   ├── parser.py                # Resume Upload & Parse
    │   └── settings.py             # Account Settings & Delete
    │
    ├── services/                    # Business logic layer
    │   ├── auth_service.py          # bcrypt hashing
    │   ├── resume_service.py        # Resume AI pipeline
    │   ├── portfolio_service.py     # Portfolio builder
    │   └── pdf_service.py           # PDF generation
    │
    ├── ai/                          # AI modules
    │   ├── resume_parser.py         # PDF/DOCX parsing
    │   ├── skill_extractor.py       # spaCy skill extraction
    │   └── text_generator.py        # Summary, cover letter NLG
    │
    ├── ml/                          # ML modules
    │   └── ats_scorer.py            # ATS score, JD match, classification
    │
    ├── utils/
    │   ├── jwt_helper.py            # JWT token management
    │   └── validators.py            # Input sanitisation & validation
    │
    ├── templates/                   # Jinja2 HTML templates
    │   ├── base.html
    │   ├── index.html
    │   ├── auth/                    # login, signup, settings
    │   ├── dashboard/
    │   ├── profile/                 # personal, education, skills, projects, experience, certifications
    │   ├── resume/                  # index, generate, edit, preview, pdf_template, upload_parse
    │   ├── cover_letter/            # index, generate, edit
    │   ├── portfolio/               # index, generate, edit, view
    │   └── errors/                  # 404, 500
    │
    └── static/
        ├── css/style.css
        ├── js/main.js
        └── uploads/                 # User uploaded files
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-resume-builder.git
cd ai-resume-builder
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and set your values:

```env
FLASK_ENV=development
SECRET_KEY=your-strong-secret-key-here
JWT_SECRET_KEY=your-strong-jwt-secret-here
DEV_DATABASE_URL=sqlite:///absolute/path/to/instance/dev.db
```

### 6. Run the Application

```bash
python run.py
```

Open your browser and go to: **http://localhost:5000**

---

### PDF Download Setup (Optional)

For PDF resume downloads, install WeasyPrint:

```bash
pip install weasyprint
```

> **Windows users:** WeasyPrint requires the GTK runtime.
> Download it from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

Alternatively, xhtml2pdf works as a lightweight fallback:

```bash
pip install xhtml2pdf
```

---

## 🗄 Database Schema

```
users
  └── profiles (1:1)
        ├── education     (1:many)
        ├── skills        (1:many)
        ├── projects      (1:many)
        ├── experience    (1:many)
        └── certifications (1:many)

users
  ├── resumes       (1:many)
  ├── cover_letters (1:many)
  └── portfolios    (1:many)
```

All relationships use `cascade="all, delete-orphan"` — deleting a user removes all their data automatically.

---

## 🔒 Security (CIA Triad)

| Dimension | Implementation |
|---|---|
| **Confidentiality** | PyJWT tokens, bcrypt password hashing, `.env` secrets, session-based token storage |
| **Integrity** | SQLAlchemy ORM (no raw SQL = no SQL injection), `html.escape()` XSS prevention, Flask-WTF CSRF tokens on every form, input length limits |
| **Availability** | Global 404/500 error handlers, rotating file logging, Flask-Limiter rate limiting (200/day, 60/hour) |

---

## 🌐 API Routes

| Method | Route | Description | Auth |
|---|---|---|---|
| GET | `/` | Landing page | No |
| GET/POST | `/auth/signup` | Register new account | No |
| GET/POST | `/auth/login` | Login | No |
| GET | `/auth/logout` | Logout | Yes |
| GET/POST | `/settings/` | Account settings | Yes |
| POST | `/settings/delete-account` | Delete account | Yes |
| GET | `/dashboard/` | Dashboard | Yes |
| GET/POST | `/profile/` | Personal details | Yes |
| GET/POST | `/profile/education` | Education CRUD | Yes |
| GET/POST | `/profile/skills` | Skills CRUD | Yes |
| GET/POST | `/profile/projects` | Projects CRUD | Yes |
| GET/POST | `/profile/experience` | Experience CRUD | Yes |
| GET/POST | `/profile/certifications` | Certifications CRUD | Yes |
| GET | `/resume/` | My resumes list | Yes |
| GET/POST | `/resume/generate` | Generate new resume | Yes |
| GET/POST | `/resume/<id>/edit` | Edit resume | Yes |
| GET | `/resume/<id>/preview` | Preview resume | Yes |
| GET | `/resume/<id>/download` | Download PDF | Yes |
| POST | `/resume/<id>/delete` | Delete resume | Yes |
| GET | `/cover-letter/` | My cover letters | Yes |
| GET/POST | `/cover-letter/generate` | Generate cover letter | Yes |
| GET/POST | `/cover-letter/<id>/edit` | Edit cover letter | Yes |
| GET | `/portfolio/` | My portfolios | Yes |
| GET/POST | `/portfolio/generate` | Generate portfolio | Yes |
| GET/POST | `/portfolio/<id>/edit` | Edit portfolio | Yes |
| GET | `/portfolio/<id>/view` | Public portfolio view | No |
| GET/POST | `/parser/upload` | Upload & parse resume | Yes |

---

## 🚀 Production Deployment

```bash
# Set environment
export FLASK_ENV=production
export SECRET_KEY=your-production-secret
export JWT_SECRET_KEY=your-production-jwt-secret
export DATABASE_URL=postgresql://user:password@host:5432/ai_resume_db

# Install gunicorn
pip install gunicorn

# Run with gunicorn (4 workers)
gunicorn "app:create_app('production')" -w 4 -b 0.0.0.0:8000
```

---

## 🧪 Running Tests

```bash
python test_app.py
```

Runs 77 tests covering:
- Input validators
- bcrypt auth service
- JWT token creation and verification
- AI skill extraction
- NLG text generation
- Resume parser
- ML ATS scoring and JD matching
- Database ORM operations
- Full resume AI pipeline
- All HTTP routes (authenticated and unauthenticated)

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch — `git checkout -b feature/your-feature`
3. Commit your changes — `git commit -m "Add your feature"`
4. Push to the branch — `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👨‍💻 Author

**Pratyaksha Sahu**
- GitHub: [@your-username](https://github.com/PratyakshaSahu-22)
- LinkedIn: [your-linkedin](https://www.linkedin.com/in/pratyaksha-sahu-a70939344)

---

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2026 Pratyaksha Sahu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">
  <sub>Built with Flask · Python AI/ML · Bootstrap 5</sub>
</div>
