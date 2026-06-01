"""
TalentLens - Unified Streamlit App for Resume Classification & Analysis
Merges FastAPI backend logic into single-port Streamlit app for HF Spaces.
"""

import logging
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Silence noisy transformers logs
logging.getLogger("transformers").setLevel(logging.ERROR)

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from db import init_db, save_analysis, get_history  # noqa: E402
from utils.extract import extract_text_pdf  # noqa: E402
from utils.preprocess import clean_text  # noqa: E402
from utils.huggingface_utils import summarize_resume_with_hf  # noqa: E402

logger = logging.getLogger(__name__)
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)

# Initialize database
init_db()

# Model paths
MODEL_PATH = BASE_DIR / "models" / "resume_classifier.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "vectorizer.pkl"

# Skill & domain keywords
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


# ============================================================================
# Backend Logic (formerly in api/main.py)
# ============================================================================


def load_classifier_assets():
    """Load pre-trained classifier model and vectorizer."""
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
    """Extract text from uploaded file (PDF support)."""
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
    """Infer category using keyword-based scoring."""
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
    """Classify resume text into category."""
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
    """Extract skills from resume text."""
    cleaned = clean_text(text)
    found = []

    for skill, terms in SKILL_KEYWORDS.items():
        if any(term in cleaned for term in terms):
            found.append(skill)

    if not found and len(cleaned.split()) > 10:
        found.append("communication")

    return sorted(set(found))


def _extract_strengths(text: str) -> list[str]:
    """Extract core strengths from resume text."""
    cleaned = clean_text(text)
    strengths = []

    for strength, terms in STRENGTH_KEYWORDS.items():
        if any(term in cleaned for term in terms):
            strengths.append(strength)

    return strengths[:4]


def _summarize_resume(text: str, category: str) -> str:
    """Generate AI-powered or heuristic resume summary."""
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
    """Generate a numerical match score (0-100)."""
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
    """Run full semantic analysis on resume text."""
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


# ============================================================================
# Streamlit UI (formerly in ui/app.py)
# ============================================================================


@st.cache_resource
def init_streamlit():
    """Initialize Streamlit config."""
    st.set_page_config(
        page_title="TalentLens - AI Resume Classifier",
        page_icon="📄",
        layout="wide",
    )


def score_band(score):
    """Return score band label."""
    if score is None:
        return "Unavailable"
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Good"
    return "Needs work"


def score_reason(score):
    """Return explanation for score."""
    if score is None:
        return "No score available yet."
    if score >= 80:
        return (
            "This resume shows strong keyword alignment and a clear "
            "skills signal for the target role."
        )
    if score >= 60:
        return (
            "This resume is promising, but it would benefit from more "
            "role-specific keywords and measurable impact statements."
        )
    return (
        "This resume needs stronger role targeting, clearer metrics, and "
        "more explicit skills alignment."
    )


def build_improvement_tips(score, skills, suggested_roles):
    """Build list of improvement suggestions."""
    tips = []

    if score is not None and score < 70:
        tips.append(
            "Add quantified wins and stronger role-specific keywords."
        )

    if len(skills) < 4:
        tips.append(
            "Expand the skills section with tools, frameworks, and platforms"
            " used in the role."
        )

    if not suggested_roles:
        tips.append(
            "Tailor the summary and bullets to one or two target job families."
        )

    if not tips:
        tips.append(
            "Polish the summary so it mirrors the target role and highlights"
            " your best strengths."
        )

    return tips


def format_category(category):
    """Format category name for display."""
    if category is None:
        return "Unknown"

    text = str(category).strip()
    if not text:
        return "Unknown"

    return text.replace("_", " ").title()


def process_classification_file(uploaded_file) -> dict:
    """Process a single file for classification."""
    try:
        raw = uploaded_file.getvalue()
        text = extract_text_from_upload(
            uploaded_file.name or "resume.pdf", raw)
        category = classify_text(text)

        return {
            "Filename": uploaded_file.name,
            "Category": format_category(category),
            "Status": "Success",
        }
    except Exception as exc:
        return {
            "Filename": uploaded_file.name,
            "Category": "Error",
            "Status": f"Error: {str(exc)}",
        }


def process_analysis_file(uploaded_file) -> tuple[dict, dict | None]:
    """Process a single file for full analysis."""
    try:
        raw = uploaded_file.getvalue()
        text = extract_text_from_upload(
            uploaded_file.name or "resume.pdf", raw)
        payload = run_semantic_analysis(text)
        category = payload.get("category") or classify_text(text)
        score = payload.get("score", 0)
        skills = payload.get("skills", []) or []
        recommended_roles = payload.get("recommended_roles", []) or []

        # Save to database
        save_analysis(
            filename=uploaded_file.name or "resume.pdf",
            category=category,
            confidence=score,
            skills=skills,
            suggestion=", ".join(recommended_roles),
        )

        return payload, None
    except Exception as exc:
        return None, str(exc)


def check_service_health() -> tuple[bool, str]:
    """Check if all required services are available and functional."""
    try:
        # Check 1: Database is accessible
        get_history()

        # Check 2: Utils are loadable (already imported at module level)
        clean_text("test")

        # Check 3: Try classification logic works
        classify_text("python sql aws")

        return True, "All systems operational"
    except Exception as exc:
        logger.warning("Service health check failed: %s", exc)
        return False, f"Issue detected: {str(exc)[:50]}"


# Initialize Streamlit
init_streamlit()

# Fetch history counts
history_rows = get_history()
history_count = len(history_rows)

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.subheader("Navigation & Help")
    st.info(
        "Use the tabs in the main interface to switch between "
        "classification, full AI analysis, and saved analysis history."
    )

    st.markdown("### Quick Actions")
    st.markdown(
        "- **Upload** one or more PDF resumes\n"
        "- **Review** automatic category assignment\n"
        "- **Explore** persistent database history"
    )

    st.markdown("### About TalentLens")
    st.write("© 2026 Francis Olum — AI Resume Classifier™")
    st.write("Analytics Engineer & Open‑Source Advocate")
    st.write(
        "🐙GitHub: "
        "[frankTheCodeBoy](https://github.com/frankTheCodeBoy)"
    )

# ============================================================================
# HEADER
# ============================================================================
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("📄 TalentLens")
    st.caption(
        "Modern, automated resume intake, classification, and scoring."
    )
with header_col2:
    service_healthy, health_msg = check_service_health()
    if service_healthy:
        st.success("● Service Online")
    else:
        st.warning(f"⚠ Service Issue: {health_msg}")

# ============================================================================
# HERO SECTION
# ============================================================================
with st.container(border=True):
    st.markdown("#### AI Document Classifier")
    st.markdown(
        "Upload a resume and get automatic category prediction and "
        "AI-driven alignment insights instantly. This workflow is "
        "optimized for PDF uploads and is designed to streamline "
        "candidate intake and resume filtering."
    )

    # KPI Grid
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(
            "Stored Analyses",
            f"{history_count} records",
            help="Persisted locally in SQLite database",
        )
    with kpi_col2:
        st.metric(
            "Current Modes",
            "3 Active Tabs",
            help="Classification, AI Analysis, and History",
        )
    with kpi_col3:
        st.metric(
            "Platform Status",
            "Fully Native UI",
            help="Single-port Streamlit app for HF Spaces",
        )

# ============================================================================
# HOW IT WORKS
# ============================================================================
with st.container(border=True):
    st.markdown("#### How it works")
    step_col1, step_col2, step_col3 = st.columns(3)
    with step_col1:
        st.markdown("**Step 1: Upload**")
        st.caption(
            "Upload PDF resumes for fast-path category prediction only."
        )
    with step_col2:
        st.markdown("**Step 2: AI Analysis**")
        st.caption(
            "Run detailed AI analysis to extract skills, strengths, "
            "suggested roles, and a numerical score."
        )
    with step_col3:
        st.markdown("**Step 3: History**")
        st.caption(
            "Explore, search, and filter previously scanned resumes "
            "with automatic persistence."
        )

st.markdown("---")

# ============================================================================
# MAIN TABS
# ============================================================================
classification_tab, analysis_tab, history_tab = st.tabs(
    ["🔍 Classification", "🤖 AI Analysis", "📜 History"]
)

# ============================================================================
# TAB 1: CLASSIFICATION
# ============================================================================
with classification_tab:
    st.subheader("Fast Resume Classification")
    st.write(
        "Use this tab when you need a fast category prediction "
        "without extra metrics."
    )

    classification_files = st.file_uploader(
        "Upload resumes for classification",
        type=["pdf"],
        accept_multiple_files=True,
        key="classification_uploader",
    )
    run_classification = st.button(
        "Classify selected files",
        disabled=not classification_files,
        width="stretch",
    )

    if classification_files and run_classification:
        classification_results = []
        for uploaded_file in classification_files:
            with st.spinner(f"Classifying {uploaded_file.name}..."):
                result = process_classification_file(uploaded_file)
                classification_results.append(result)

        classification_df = pd.DataFrame(classification_results)
        st.dataframe(classification_df, width="stretch")

        if not classification_df.empty:
            st.bar_chart(classification_df["Category"].value_counts())

        failed = classification_df[classification_df["Status"] != "Success"]
        if not failed.empty:
            st.warning(
                "Some classification uploads failed. Review the Status column."
            )
    elif classification_files:
        st.info(
            "Select one or more PDF resumes and click "
            "**Classify selected files** to run the request."
        )
    else:
        st.info("Select one or more PDF resumes to classify.")

# ============================================================================
# TAB 2: ANALYSIS
# ============================================================================
with analysis_tab:
    st.subheader("Deep AI Analysis")
    st.write(
        "Use this tab to extract candidate skills, core strengths, "
        "suggested roles, and a matching score."
    )

    analysis_files = st.file_uploader(
        "Upload resumes for AI analysis",
        type=["pdf"],
        accept_multiple_files=True,
        key="analysis_uploader",
    )
    run_analysis = st.button(
        "Analyze selected files",
        disabled=not analysis_files,
        width="stretch",
    )

    if analysis_files and run_analysis:
        analysis_results = []
        for uploaded_file in analysis_files:
            with st.spinner(f"Analyzing {uploaded_file.name}..."):
                analyze_payload, error = process_analysis_file(uploaded_file)

                if error:
                    analysis_results.append(
                        {
                            "Filename": uploaded_file.name,
                            "Category": "Error",
                            "Confidence": None,
                            "Confidence Band": "Unavailable",
                            "Skills": "",
                            "Suggestions": error,
                            "Strengths": "",
                            "Improvement Tips": "",
                        }
                    )
                    continue

                skills = analyze_payload.get("skills") or []
                suggested_roles = (
                    analyze_payload.get("recommended_roles") or []
                )
                strengths = analyze_payload.get("strengths") or []
                summary = (
                    analyze_payload.get("summary")
                    or "No summary available."
                )
                score = analyze_payload.get("score")
                score_value = int(score) if isinstance(
                    score, (int, float)
                ) else None

                improvement_tips = build_improvement_tips(
                    score_value,
                    skills,
                    suggested_roles,
                )

                analysis_results.append(
                    {
                        "Filename": uploaded_file.name,
                        "Category": format_category(
                            analyze_payload.get("category")
                        ),
                        "Confidence": score_value,
                        "Confidence Band": score_band(score_value),
                        "Skills": ", ".join(skills),
                        "Suggestions": ", ".join(suggested_roles),
                        "Strengths": ", ".join(strengths),
                        "Improvement Tips": " | ".join(improvement_tips),
                    }
                )

                # Render detailed analysis card
                with st.container(border=True):
                    res_header_col1, res_header_col2 = st.columns([3, 1])
                    with res_header_col1:
                        st.markdown(f"### {uploaded_file.name}")
                        formatted_cat = format_category(
                            analyze_payload.get("category")
                        )
                        st.markdown(
                            f"**Predicted Category:** {formatted_cat}"
                        )
                        st.markdown(f"*Summary:* {summary}")
                        st.markdown(
                            f"*Score Reason:* {score_reason(score_value)}"
                        )
                    with res_header_col2:
                        band = score_band(score_value)
                        val_str = (
                            f"{score_value}"
                            if score_value is not None
                            else "N/A"
                        )
                        is_good = score_value and score_value >= 60
                        st.metric(
                            label="Match Score",
                            value=val_str,
                            delta=band,
                            delta_color="normal" if is_good else "inverse",
                        )

                    st.divider()

                    details_col1, details_col2, details_col3 = st.columns(3)
                    with details_col1:
                        st.markdown("**Suggested Roles**")
                        st.write(
                            ", ".join(suggested_roles)
                            if suggested_roles
                            else "No roles suggested."
                        )
                    with details_col2:
                        st.markdown("**Strengths**")
                        st.write(
                            ", ".join(strengths)
                            if strengths
                            else "No strengths detected."
                        )
                    with details_col3:
                        st.markdown("**Skills**")
                        st.write(
                            ", ".join(skills)
                            if skills
                            else "No skills detected."
                        )

                    st.markdown("**Suggested Improvement Tips**")
                    for tip in improvement_tips:
                        st.markdown(f"- {tip}")

        analysis_df = pd.DataFrame(analysis_results)
        st.subheader("Summary Table")
        st.dataframe(analysis_df, width="stretch")

        if not analysis_df.empty:
            scored_df = analysis_df.dropna(subset=["Confidence"])
            if not scored_df.empty:
                st.subheader("Score Distribution")
                st.bar_chart(
                    scored_df["Confidence"].value_counts().sort_index()
                )

            st.subheader("Suggestion Focus")
            st.bar_chart(
                analysis_df["Suggestions"].value_counts().sort_index()
            )

            st.subheader("Confidence Band")
            st.bar_chart(
                analysis_df["Confidence Band"].value_counts().sort_index()
            )

            tip_counter = Counter()
            for tips in analysis_df["Improvement Tips"].dropna():
                for tip in str(tips).split(" | "):
                    cleaned_tip = tip.strip()
                    if cleaned_tip:
                        tip_counter[cleaned_tip] += 1

            if tip_counter:
                st.subheader("Cross-Resume Improvement Priorities")
                for tip, count in tip_counter.most_common(5):
                    st.write(f"- {tip} ({count} resume(s))")
    elif analysis_files:
        st.info(
            "Select one or more PDF resumes and click "
            "**Analyze selected files** to run the request."
        )
    else:
        st.info("Select one or more PDF resumes for AI analysis.")

# ============================================================================
# TAB 3: HISTORY
# ============================================================================
with history_tab:
    st.subheader("Past Analyses History")
    history_rows = get_history()

    if history_rows:
        history_df = pd.DataFrame(
            history_rows,
            columns=[
                "ID",
                "Filename",
                "Category",
                "Confidence",
                "Skills",
                "Suggestion",
                "Timestamp",
            ],
        )

        # Filters
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        with filter_col1:
            search_query = st.text_input(
                "Search text",
                placeholder="Filename, category, suggestion...",
                key="history_search_input",
            ).strip()
        with filter_col2:
            category_options = ["All"] + sorted(
                history_df["Category"].dropna().unique().tolist()
            )
            selected_category = st.selectbox(
                "Category Filter",
                category_options,
                key="history_category_select",
            )
        with filter_col3:
            start_date = st.date_input("From Date", key="history_start_date")
        with filter_col4:
            end_date = st.date_input("To Date", key="history_end_date")

        filtered_df = history_df.copy()

        if selected_category != "All":
            filtered_df = filtered_df[
                filtered_df["Category"] == selected_category
            ]

        if start_date and end_date:
            filtered_df["Timestamp"] = pd.to_datetime(
                filtered_df["Timestamp"], errors="coerce"
            )
            filtered_df = filtered_df[
                (filtered_df["Timestamp"].dt.date >= start_date)
                & (filtered_df["Timestamp"].dt.date <= end_date)
            ]

        if search_query:
            search_mask = filtered_df.apply(
                lambda row: search_query.lower()
                in str(row.to_dict()).lower(),
                axis=1,
            )
            filtered_df = filtered_df[search_mask]

        if filtered_df.empty:
            st.info("No matching analyses found for the current filters.")
        else:
            st.dataframe(filtered_df, width="stretch")
    else:
        st.info("No analyses stored yet.")
