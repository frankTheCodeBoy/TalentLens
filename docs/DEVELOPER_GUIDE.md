# Developer Guide

This guide is for developers who want to run, extend, and retrain the resume classifier.

## 1. Project overview

The app is a lightweight resume analysis workflow built with:

- **FastAPI** for the backend API
- **Streamlit** for the local web UI
- **SQLite** for local history storage
- **scikit-learn** for the classifier
- **joblib** for model persistence
- **PyMuPDF / python-docx** for document extraction

### Main entry points

- Backend: `api/main.py`
- Frontend: `ui/app.py`
- Training script: `scripts/train_classifier.py`
- Manual registration helper: `scripts/register_training_samples.py`

### Runtime behavior

1. The Streamlit UI uploads a PDF resume.
2. The backend extracts text from the PDF.
3. The backend classifies the resume using the trained model.
4. The backend returns skills, strengths, recommended roles, and a score.
5. The UI displays the result and stores the analysis locally in SQLite.

## 2. Environment setup

### Requirements

- Python 3.11
- Windows PowerShell (the commands below are written for PowerShell)

### Create and activate the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file at the project root if you need to override defaults.

Recommended variables:

```env
CLASSIFY_API_URL=http://127.0.0.1:8000/classify
ANALYZE_API_URL=http://127.0.0.1:8000/analyze
ALLOWED_ORIGINS=http://localhost:8501
```

If you do not create `.env`, the app falls back to the defaults in the code.

## 3. Start the application

### Option A: Start backend and UI separately

#### Start the backend

```powershell
.\.venv\Scripts\python api/main.py
```

The API will run on `http://127.0.0.1:8000`.

#### Start the Streamlit UI

```powershell
.\.venv\Scripts\streamlit run ui/app.py --server.headless true --server.port 8501
```

The UI will run on `http://localhost:8501`.

### Option B: Run with Uvicorn directly

If you prefer launching the FastAPI app directly:

```powershell
.\.venv\Scripts\uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

## 4. Verify the app is running

### Backend health check

```powershell
curl http://127.0.0.1:8000/
```

Expected response:

```json
{"status":"ok","service":"resume classifier"}
```

### Streamlit check

Open `http://localhost:8501` in a browser.

## 5. Project structure

```text
api/
  main.py
  
data/
  raw/
  training_manifest.json

docs/
  DEVELOPER_GUIDE.md

models/
  resume_classifier.pkl
  vectorizer.pkl

scripts/
  train_classifier.py
  register_training_samples.py

ui/
  app.py

utils/
  extract.py
  preprocess.py
```

## 6. Training workflow

### Important note

You **do not need to open the notebook** to train the classifier.
The notebook is optional and is not required for retraining.

### Add new training data

1. Put a new resume in `data/raw/`.
2. Register it in `data/training_manifest.json`.
3. Retrain the classifier.

### Register a file manually

```powershell
python scripts/register_training_samples.py data/raw/your_resume.pdf --category YourCategory
```

### Register and retrain in one step

```powershell
python scripts/register_training_samples.py data/raw/your_resume.pdf --category YourCategory --retrain
```

### Retrain without registering

```powershell
python scripts/train_classifier.py
```

### Current training behavior

- The manifest is the source of truth for labeled training data.
- The classifier is a lightweight `LogisticRegression` model over TF-IDF text features.
- New categories are added by adding a new manifest label and retraining.
- The current workflow is designed for local experimentation and small-to-medium training sets.

## 7. How the UI works

The Streamlit app offers three tabs:

1. **Classification**
   - Upload a PDF resume.
   - Get a predicted category.

2. **AI Analysis**
   - Upload a PDF resume.
   - Get skills, strengths, suggested roles, and a score.

3. **History**
   - Review saved analyses stored in SQLite.
   - Search and filter by filename, category, and date.

## 8. How the backend works

### `/classify`

- Accepts an uploaded PDF.
- Extracts text.
- Runs the trained classifier.
- Returns `category` and `source`.

### `/analyze`

- Accepts an uploaded PDF.
- Extracts text.
- Runs local semantic analysis.
- Returns `category`, `summary`, `skills`, `recommended_roles`, `strengths`, `score`, and `source`.
- Saves the result into SQLite history.

## 9. Model and data notes

### Model artifacts

- `models/resume_classifier.pkl`
- `models/vectorizer.pkl`

### Manifest

- `data/training_manifest.json`

The manifest stores `filename -> category` mappings and must be kept in sync with the files present in `data/raw/`.

## 10. Current limits

- The UI currently accepts **PDF uploads only**.
- The classifier is a **local heuristic + TF-IDF pipeline**, not a large language model.
- The semantic analysis logic is **rule-based** and should be treated as a lightweight scoring aid.
- The app is intended for **local development**, not a production deployment.
- The current training approach is best for a **small and curated set of categories**.

## 11. Troubleshooting

### Backend import issues

If the backend fails to start because local imports are missing:

- Confirm you are running from the project root.
- Confirm `.venv` is activated.
- Check that `api/main.py` is adding the project root to `sys.path` before importing local modules.

### Streamlit cannot reach the API

- Confirm the backend is running on `http://127.0.0.1:8000`.
- Confirm `ALLOWED_ORIGINS` includes `http://localhost:8501`.
- Confirm the UI points to the correct endpoint values.

### Training does not include a new file

- Confirm the file exists in `data/raw/`.
- Confirm the manifest entry was added.
- Re-run `python scripts/train_classifier.py`.

## 12. Recommended development workflow

1. Activate `.venv`.
2. Start the backend.
3. Start the UI.
4. Upload a PDF and validate the response.
5. Add new labeled samples to `data/raw/`.
6. Register the samples.
7. Retrain the classifier.
8. Re-test the API with a real resume upload.

## 13. Quick commands

```powershell
# Setup
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Run backend
.\.venv\Scripts\python api/main.py

# Run UI
.\.venv\Scripts\streamlit run ui/app.py --server.headless true --server.port 8501

# Retrain
python scripts/train_classifier.py
```
