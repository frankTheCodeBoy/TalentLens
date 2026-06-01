# 🧪 TalentLens - AI Resume Classifier

> **Streamlit-native resume classification and analysis tool** deployed on Hugging Face Spaces.  
> Single-port, production-ready application with full AI-powered analysis.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-orange?style=for-the-badge&logo=streamlit)](#)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-FFD21E?style=for-the-badge&logo=huggingface)](#)

---

## ✨ What is This?

**TalentLens** is a modern, automated resume intake, classification, and scoring application.  
It provides:

- **Fast Classification** → Quick category prediction (Tech, Finance, Healthcare, Education, etc.)
- **Deep AI Analysis** → Full extraction of skills, strengths, recommended roles, and a numerical match score
- **Persistent History** → All analyses stored locally in SQLite for audit & exploration

The app is optimized for **Hugging Face Spaces** with a single Streamlit entry point on port **7860**.

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.10+
- pip or uv package manager

### Installation

```bash
# Clone and setup
git clone https://github.com/frankTheCodeBoy/TalentLens.git
cd TalentLens
cp .env.example .env

# Add your Hugging Face API key to .env (optional, for AI summaries)
# HUGGINGFACE_API_KEY=hf_your_token_here

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open in your browser at **<http://localhost:8501>**.

---

## 📱 Features

### Tab 1: Fast Classification

- Upload single or multiple PDF resumes
- Get instant category prediction
- View category distribution charts

### Tab 2: Deep AI Analysis

- Extract skills, strengths, and recommended roles
- Get numerical match scores (0-100)
- Receive improvement suggestions
- View cross-resume analytics

### Tab 3: History & Search

- Browse all past analyses
- Filter by category, date range, or keyword
- Persistent SQLite database for audit trail

---

## 🌍 Deployment to Hugging Face Spaces

### Option 1: Docker (Recommended)

HF Spaces automatically detects and builds from the `Dockerfile`:

```bash
git push origin main
# HF Spaces will automatically build and deploy
```

### Option 2: Manual Setup on HF Spaces

1. Create a new **Streamlit** space on HF Spaces
2. Add your repository as the source
3. HF will auto-detect `Dockerfile` and build
4. Set `HUGGINGFACE_API_KEY` secret in Space settings (if using AI summaries)
5. Space will deploy to `https://<username>-<space-name>.hf.space`

### Environment Variables

In HF Spaces **Secrets** tab, add:

```
HUGGINGFACE_API_KEY=hf_xxxxxxxxx  # Optional, for AI-powered summaries
```

---

## 📚 Architecture

### Single-Port Design (Streamlit-Only)

```
app.py (29KB)
  ├─ Backend Logic (formerly api/main.py)
  │   ├── Classification & scoring
  │   ├── Text extraction & preprocessing
  │   └── Hugging Face API integration
  │
  ├─ UI Layer (formerly ui/app.py)
  │   ├── File upload & processing
  │   ├── Results rendering
  │   └── History browser
  │
  └─ Utils
      ├── extract.py (PDF text extraction)
      ├── preprocess.py (text cleaning)
      └── huggingface_utils.py (AI summaries)
```

### Data Flow

1. User uploads PDF resume
2. `extract_text_pdf()` → Raw text extraction
3. `clean_text()` → Preprocessing
4. `classify_text()` → Category prediction (model or keyword-based)
5. `run_semantic_analysis()` → Full analysis (skills, strengths, scoring)
6. `save_analysis()` → Persist to SQLite
7. UI renders results & analytics

---

## 🔧 Configuration

### Model Assets

Pre-trained classifier files (optional):

```
models/
  ├── resume_classifier.pkl   (sklearn model)
  └── vectorizer.pkl          (TF-IDF vectorizer)
```

If models are missing, the app falls back to keyword-based inference.

### Database

SQLite database is auto-created on first run:

```
resume_analysis.db
  └── analyses (
        id, filename, category, confidence, 
        skills, suggestion, timestamp
      )
```

---

## 🧠 How Classification Works

### Method 1: Pre-trained Model (if available)

- Loads `resume_classifier.pkl` and `vectorizer.pkl`
- Uses TF-IDF vectorization + ML prediction
- Fast and accurate for trained categories

### Method 2: Keyword-Based Fallback

- Scores resume against category keywords:
  - `python`, `sql`, `ai`, `cloud` → Tech
  - `finance`, `accounting`, `budget` → Finance
  - `healthcare`, `patient`, `clinical` → Health
  - `teaching`, `curriculum`, `student` → Education
- Returns highest-scoring category
- Provides consistent results without model dependency

### AI Summaries (Optional)

If `HUGGINGFACE_API_KEY` is set, uses Hugging Face API for intelligent summaries.  
Falls back to rule-based summaries if API unavailable or no key provided.

---

## 📊 Scoring Algorithm

**Base score: 55/100**

| Factor | Points |
|--------|--------|
| Non-"general" category | +12 |
| Each skill (max 4) | +4 each |
| Technical terms | +8 |
| Leadership terms | +5 |
| Domain-specific terms | +4 |

**Range:** 55–100 (capped at 100)

---

## 🗂️ Project Structure

```
TalentLens/
├── app.py                 # ⭐ Single Streamlit entry point
├── requirements.txt       # Dependencies
├── Dockerfile             # HF Spaces container
├── .env.example          # Environment template
├── .env                  # Secrets (git-ignored)
│
├── db.py                 # SQLite operations
├── resume_analysis.db    # Local database
│
├── models/
│   ├── resume_classifier.pkl
│   └── vectorizer.pkl
│
├── utils/
│   ├── extract.py        # PDF text extraction
│   ├── preprocess.py     # Text cleaning
│   └── huggingface_utils.py  # HF API integration
│
├── tests/                # Pytest suite
├── notebooks/            # Jupyter notebooks
└── docs/                 # Additional docs
```

---

## 🧪 Testing

Run tests locally:

```bash
pytest tests/ -v
pytest tests/ --cov=.
```

---

## 🌟 Performance Notes

- **Classification:** <1 second per file
- **Full Analysis:** 1-3 seconds per file (without AI summary)
- **AI Summary:** 2-5 seconds (with HUGGINGFACE_API_KEY)
- **Memory:** ~500MB per pod on HF Spaces (accounts for transformers)
- **Database:** SQLite handles 100K+ records efficiently

---

## 🐛 Troubleshooting

### "Backend Offline" error

- This was for the old FastAPI setup. TalentLens runs everything in Streamlit.
- If app won't start, check logs: `streamlit run app.py --logger.level=debug`

### Import errors

- Ensure `PYTHONPATH=/app` is set
- Run `pip install -r requirements.txt` again

### PDF extraction fails

- Ensure `pymupdf` is installed: `pip install pymupdf`
- Check PDF is not corrupted or encrypted

### Hugging Face API errors

- Verify `HUGGINGFACE_API_KEY` is set correctly (in `.env` locally, or Secrets in HF)
- App will gracefully fall back to keyword-based summaries if API unavailable

---

## 📈 What's New in TalentLens

**vs. ai_doc_classifier (original):**

- ✅ Single Streamlit port (7860) — no FastAPI needed
- ✅ Merged backend logic into `app.py`
- ✅ Removed multi-port complexity
- ✅ Simplified Docker setup
- ✅ HF Spaces-native deployment
- ✅ Same functionality & behavior preserved
- ✅ Cleaner codebase, easier to maintain

---

## 👤 Author

**Built by:** Francis Olum  
**GitHub:** [@frankTheCodeBoy](https://github.com/frankTheCodeBoy)  
**Role:** Analytics Engineer & Open‑Source Advocate

---

## 📝 License

See LICENSE file for details.
