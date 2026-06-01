import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import joblib  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from fastapi import Depends, FastAPI, Header, UploadFile  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402


from db import init_db, save_analysis  # noqa: E402
from utils.extract import extract_text_pdf  # noqa: E402
from utils.preprocess import clean_text  # noqa: E402
from utils.huggingface_utils import summarize_resume_with_hf  # noqa: E402

try:
    from openai import OpenAI  # noqa: E402
except ImportError:
    OpenAI = None

try:
    from sentence_transformers import SentenceTransformer  # noqa: E402
except ImportError:
    SentenceTransformer = None

load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)

logger = logging.getLogger(__name__)
app = FastAPI()
init_db()

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security / Auth ---
API_KEY = os.getenv("BACKEND_API_KEY", "changeme123")


def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


MODEL_PATH = BASE_DIR / "models" / "resume_classifier.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "vectorizer.pkl"

SKILL_KEYWORDS = {
    "python": ["python", "django", "flask", "fastapi"],
    "sql": ["sql", "postgres", "postgresql", "mysql", "sqlite"],
    "ai": [
        "machine learning",
        "ml",
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "ai",
    ],
    "cloud": [
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "terraform",
    ],
    "finance": ["finance", "accounting", "fp&a", "forecasting", "budget"],
    "health": ["healthcare", "patient", "medical", "clinical", "hipaa"],
    "education": [
        "teaching",
        "instruction",
        "curriculum",
        "student",
        "education",
    ],
    "engineering": [
        "engineering",
        "systems",
        "software",
        "automation",
        "devops",
    ],
}

ROLE_MAP = {
    "education": [
        "Teacher",
        "Instructional Designer",
        "Education Coordinator",
    ],
    "finance": [
        "Financial Analyst",
        "Finance Associate",
        "Accounting Specialist",
    ],
    "health": [
        "Healthcare Coordinator",
        "Medical Office Specialist",
        "Clinical Operations Associate",
    ],
    "tech": [
        "Software Engineer",
        "Data Analyst",
        "Backend Engineer",
    ],
    "general": [
        "Generalist",
        "Operations Associate",
        "Technical Support Specialist",
    ],
}

STRENGTH_KEYWORDS = {
    "communication": [
        "communication",
        "presentation",
        "stakeholder",
        "client",
    ],
    "leadership": [
        "lead",
        "led",
        "manager",
        "supervised",
        "coordinated",
    ],
    "analysis": [
        "analysis",
        "analyze",
        "forecast",
        "reporting",
        "metrics",
    ],
    "execution": [
        "implemented",
        "built",
        "delivered",
        "improved",
        "optimized",
    ],
}


def load_classifier_assets():
    model = None
    vectorizer = None

    try:
        if MODEL_PATH.exists() and VECTORIZER_PATH.exists():
            model = joblib.load(MODEL_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
    except Exception as exc:
        logger.warning("Unable to load classifier assets: %s", exc)

    return model, vectorizer


def extract_text_from_upload(filename: str, contents: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    temp_dir = Path(tempfile.gettempdir())
    temp_path = temp_dir / f"resume_upload_{Path(filename).stem}_{os.getpid()}"

    if suffix == ".pdf":
        temp_path = temp_path.with_suffix(".pdf")
    else:
        raise ValueError(f"Unsupported file type: {suffix or filename}")

    try:
        temp_path.write_bytes(contents)
        if suffix == ".pdf":
            return extract_text_pdf(str(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _infer_category_from_text(text: str) -> str:
    cleaned = clean_text(text)
    score_map = {
        "education": 0,
        "finance": 0,
        "health": 0,
        "tech": 0,
    }

    for category, terms in SKILL_KEYWORDS.items():
        for term in terms:
            if term in cleaned:
                if category in score_map:
                    score_map[category] += 1
                elif category == "ai":
                    score_map["tech"] += 1

    if cleaned.count("python") >= 2 or cleaned.count("sql") >= 2:
        score_map["tech"] += 2

    health_terms = (
        cleaned.count("healthcare")
        or cleaned.count("patient")
        or cleaned.count("clinical")
    )
    if health_terms:
        score_map["health"] += 2

    finance_terms = (
        cleaned.count("finance")
        or cleaned.count("accounting")
        or cleaned.count("budget")
    )
    if finance_terms:
        score_map["finance"] += 2

    education_terms = (
        cleaned.count("teaching")
        or cleaned.count("curriculum")
        or cleaned.count("student")
    )
    if education_terms:
        score_map["education"] += 2

    best_category = max(score_map, key=score_map.get)
    if score_map[best_category] == 0:
        return "general"
    return best_category


def classify_text(text: str) -> str:
    model, vectorizer = load_classifier_assets()
    if model is not None and vectorizer is not None:
        try:
            features = vectorizer.transform([clean_text(text)])
            prediction = model.predict(features)[0]
            if isinstance(prediction, str) and prediction:
                normalized = prediction.strip().lower()
                if normalized:
                    return normalized
        except Exception as exc:
            logger.warning("Model prediction failed: %s", exc)

    return _infer_category_from_text(text)


def _extract_skills(text: str) -> list[str]:
    cleaned = clean_text(text)
    found = []

    for skill, terms in SKILL_KEYWORDS.items():
        if any(term in cleaned for term in terms):
            found.append(skill)

    if not found and len(cleaned.split()) > 10:
        found.append("communication")

    return sorted(set(found))


def _extract_strengths(text: str) -> list[str]:
    cleaned = clean_text(text)
    strengths = []

    for strength, terms in STRENGTH_KEYWORDS.items():
        if any(term in cleaned for term in terms):
            strengths.append(strength)

    return strengths[:4]


def _summarize_resume(text: str, category: str) -> str:
    cleaned = clean_text(text)
    top_skills = _extract_skills(text)

    # Try Hugging Face API first for AI-powered summary
    hf_summary = summarize_resume_with_hf(text)
    if hf_summary:
        return hf_summary

    if not top_skills:
        return (
            "This "
            f"{category} resume appears to be a general document "
            "with limited extracted keywords."
        )

    summary = f"This {category} resume highlights {', '.join(top_skills)}."

    if "python" in cleaned or "sql" in cleaned:
        summary += (
            " The document emphasizes technical execution and "
            "data-oriented work."
        )
    if "teacher" in cleaned or "curriculum" in cleaned:
        summary += (
            " The language suggests teaching, mentoring, and "
            "instructional design experience."
        )
    if "budget" in cleaned or "finance" in cleaned:
        summary += (
            " The resume includes financial, reporting, or "
            "planning responsibilities."
        )

    return summary


def _score_resume(text: str, category: str, skills: list[str]) -> float:
    cleaned = clean_text(text)
    score = 55.0

    if category != "general":
        score += 12.0

    score += min(18.0, len(skills) * 4)

    technical_terms = ["python", "sql", "aws", "azure", "docker", "excel"]
    leadership_terms = [
        "leader",
        "managed",
        "coordinated",
        "improved",
        "implemented",
    ]
    domain_terms = [
        "metrics",
        "budget",
        "forecast",
        "patient",
        "clinical",
        "student",
    ]

    if any(term in cleaned for term in technical_terms):
        score += 8.0

    if any(term in cleaned for term in leadership_terms):
        score += 5.0

    if any(term in cleaned for term in domain_terms):
        score += 4.0

    return round(min(100.0, score), 2)


def run_semantic_analysis(text: str) -> dict[str, Any]:
    category = classify_text(text)
    if category == "general":
        category = "tech"

    skills = _extract_skills(text)
    strengths = _extract_strengths(text)
    summary = _summarize_resume(text, category)
    score = _score_resume(text, category, skills)
    recommended_roles = ROLE_MAP.get(category, ROLE_MAP["general"])

    return {
        "category": category,
        "summary": summary,
        "skills": skills,
        "recommended_roles": recommended_roles,
        "strengths": strengths,
        "score": score,
        "source": "local",
    }


@app.post("/classify")
async def classify_endpoint(
 file: UploadFile, _: bool = Depends(verify_api_key)):
    raw = await file.read()
    text = extract_text_from_upload(file.filename or "resume.pdf", raw)
    category = classify_text(text)

    return {
        "category": category,
        "source": "local",
    }


@app.post("/analyze")
async def analyze_endpoint(
 file: UploadFile, _: bool = Depends(verify_api_key)):
    raw = await file.read()
    text = extract_text_from_upload(file.filename or "resume.pdf", raw)
    payload = run_semantic_analysis(text)
    category = payload.get("category") or classify_text(text)
    score = payload.get("score", 0)
    skills = payload.get("skills", []) or []
    recommended_roles = payload.get("recommended_roles", []) or []

    save_analysis(
        filename=file.filename or "resume.pdf",
        category=category,
        confidence=score,
        skills=skills,
        suggestion=", ".join(recommended_roles),
    )

    return payload


@app.get("/")
async def root(_: bool = Depends(verify_api_key)):
    return {"status": "ok", "service": "resume classifier"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
