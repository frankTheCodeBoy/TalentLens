import os
import logging
from collections import Counter
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from api.main import API_KEY
from db import get_history, init_db

# Silence noisy transformers logs
logging.getLogger("transformers").setLevel(logging.ERROR)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)

API_URL_CLASSIFY = os.getenv(
    "CLASSIFY_API_URL", "http://127.0.0.1:8000/classify"
)
API_URL_ANALYZE = os.getenv(
    "ANALYZE_API_URL",
    API_URL_CLASSIFY.replace("/classify", "/analyze"),
)

st.set_page_config(
    page_title="AI Resume Classifier",
    page_icon="📄",
    layout="wide",
)
init_db()


def make_upload_payload(uploaded_file):
    return {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/pdf",
        )
    }


def fetch_json(url, uploaded_file, timeout=30):
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    response = requests.post(
        url,
        files=make_upload_payload(uploaded_file),
        headers=headers,   # <-- add this
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Unexpected response format")
    return payload


def score_band(score):
    if score is None:
        return "Unavailable"
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Good"
    return "Needs work"


def score_reason(score):
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
    if category is None:
        return "Unknown"

    text = str(category).strip()
    if not text:
        return "Unknown"

    return text.replace("_", " ").title()


def check_backend_status():
    api_root = API_URL_CLASSIFY.replace("/classify", "/")
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    try:
        response = requests.get(api_root, headers=headers, timeout=3)
        response.raise_for_status()
        return True, None
    except requests.exceptions.RequestException as exc:
        return False, str(exc)


# Fetch history counts & backend status
history_rows = get_history()
history_count = len(history_rows)
backend_available, backend_error = check_backend_status()

# Sidebar Navigation Explanation
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

    st.markdown("### About")
    st.write("© 2026 Francis Olum — AI Resume Classifier™")
    st.write("Analytics Engineer & Open‑Source Advocate")
    st.write("🐙GitHub: [frankTheCodeBoy](https://github.com/frankTheCodeBoy)")

# Header / App Title Block
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.title("📄 AI Resume Classifier")
    st.caption(
        "Modern, automated resume intake, classification, and scoring."
    )
with header_col2:
    if backend_available:
        st.success("● Backend Online")
    else:
        st.error("● Backend Offline")

# Hero section replacing messy CSS cards
with st.container(border=True):
    st.markdown("#### AI Document Classifier")
    st.markdown(
        "Upload a resume and get automatic category prediction and "
        "AI-driven alignment insights instantly. This workflow is "
        "optimized for PDF uploads and is designed to streamline "
        "candidate intake and resume filtering."
    )

    # KPI Grid with native columns and metrics
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
            help="Removed HTML/CSS overrides for robust layout",
        )

# Instructions section
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

if not backend_available:
    st.warning(
        "Backend is currently unavailable. Uploads will fail until "
        f"the API is running. Error: {backend_error}"
    )

st.markdown("---")

# Main Tab-based View
classification_tab, analysis_tab, history_tab = st.tabs(
    ["🔍 Classification", "🤖 AI Analysis", "📜 History"]
)

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
            try:
                with st.spinner(f"Classifying {uploaded_file.name}..."):
                    payload = fetch_json(API_URL_CLASSIFY, uploaded_file)
                classification_results.append(
                    {
                        "Filename": uploaded_file.name,
                        "Category": format_category(
                            payload.get("category")
                        ),
                        "Status": "Success",
                    }
                )
            except requests.exceptions.RequestException as exc:
                classification_results.append(
                    {
                        "Filename": uploaded_file.name,
                        "Category": "Error",
                        "Status": f"Request failed: {exc}",
                    }
                )
            except ValueError:
                classification_results.append(
                    {
                        "Filename": uploaded_file.name,
                        "Category": "Error",
                        "Status": "Unexpected response format",
                    }
                )

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
            try:
                with st.spinner(f"Analyzing {uploaded_file.name}..."):
                    analyze_payload = fetch_json(
                        API_URL_ANALYZE, uploaded_file)

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
                suggested_roles_text = (
                    ", ".join(suggested_roles)
                    if suggested_roles
                    else "No roles suggested."
                )
                strengths_text = (
                    ", ".join(strengths)
                    if strengths
                    else "No strengths detected."
                )
                skills_text = (
                    ", ".join(skills)
                    if skills
                    else "No skills detected."
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

                # Render each analysis result in a beautiful native container
                with st.container(border=True):
                    res_header_col1, res_header_col2 = st.columns([3, 1])
                    with res_header_col1:
                        st.markdown(f"### {uploaded_file.name}")
                        formatted_cat = format_category(
                            analyze_payload.get("category")
                        )
                        st.markdown(f"**Predicted Category:** {formatted_cat}")
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
                        st.write(suggested_roles_text)
                    with details_col2:
                        st.markdown("**Strengths**")
                        st.write(strengths_text)
                    with details_col3:
                        st.markdown("**Skills**")
                        st.write(skills_text)

                    st.markdown("**Suggested Improvement Tips**")
                    for tip in improvement_tips:
                        st.markdown(f"- {tip}")

            except requests.exceptions.RequestException as exc:
                analysis_results.append(
                    {
                        "Filename": uploaded_file.name,
                        "Category": "Error",
                        "Confidence": None,
                        "Confidence Band": "Unavailable",
                        "Skills": "",
                        "Suggestions": f"Request failed: {exc}",
                        "Strengths": "",
                        "Improvement Tips": "",
                    }
                )
            except ValueError:
                analysis_results.append(
                    {
                        "Filename": uploaded_file.name,
                        "Category": "Error",
                        "Confidence": None,
                        "Confidence Band": "Unavailable",
                        "Skills": "",
                        "Suggestions": "Unexpected response format",
                        "Strengths": "",
                        "Improvement Tips": "",
                    }
                )

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

        # Filters laid out in nice, compact, professional columns
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
