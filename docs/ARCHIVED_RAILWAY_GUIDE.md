# ARCHIVED: Railway Deployment Configuration

**Status**: ❌ Not in use - Deployment failed

## Railway Setup

Railway is a simple cloud deployment platform with GitHub integration.

### Prerequisites
- GitHub account
- Railway account (https://railway.app)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Login with GitHub"
3. Authorize Railway

### Step 2: Create New Project
1. Click "+ New Project"
2. Select "Deploy from GitHub repo"
3. Choose: `frankTheCodeBoy/ai_doc_classifier`
4. Click "Deploy"

### Step 3: Configure Service
Railway auto-detects Dockerfile:
- Service name: `resume-classifier`
- Port: 8000 (FastAPI), 8501 (Streamlit)
- Region: Choose closest to you

### Step 4: Add Environment Variables
In Railway dashboard:
1. Go to "Variables" tab
2. Add:
   ```
   BACKEND_API_KEY=changeme123
   ALLOWED_ORIGINS=*
   CLASSIFY_API_URL=http://localhost:8000/classify
   ANALYZE_API_URL=http://localhost:8000/analyze
   HUGGINGFACE_API_KEY=<your-hf-token>
   ```
3. Click "Redeploy"

### Step 5: Get Live URL
Once deployment succeeds (green checkmark ✅):
1. Click service
2. Find "Railway Domain"
3. Access at: `https://your-domain.railway.app`

## railway.json Config
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "buildCommand": "docker build -t resume-classifier ."
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "./start.sh"
  }
}
```

## Why Not Used
- Free tier deployment issues
- Build timeouts
- Port binding conflicts

## To Reactivate
1. Re-create Railway project
2. Add environment variables
3. Monitor logs for errors
4. Troubleshoot port mapping
