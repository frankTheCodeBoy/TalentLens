# ARCHIVED: DigitalOcean Deployment Configuration

**Status**: ⚠️ Requires GitHub Student Pack credit (not credit card-free)

## DigitalOcean Setup

DigitalOcean App Platform provides reliable Docker hosting with $200 free student credit.

### Prerequisites
- GitHub Student Pack account
- DigitalOcean account (claim $200 credit)

### Step 1: Claim Student Credit
1. Go to: https://www.digitalocean.com/github-students
2. Click "Claim Free Credit"
3. Verify GitHub Student Pack
4. Receive $200 credit (~40 months free)

### Step 2: Create App Platform Project
1. DigitalOcean Dashboard → "Create" → "App"
2. Select "GitHub"
3. Choose repository: `ai_doc_classifier`
4. Select branch: `main`

### Step 3: Configure Service
DigitalOcean auto-detects Dockerfile:
- Service type: Web Service
- Source: GitHub repo
- Port: 8000 (FastAPI), 8501 (Streamlit)
- Instance type: Basic ($5/month, covered by credit)
- Region: Choose nearest (nyc, lon, etc.)

### Step 4: Set Environment Variables
1. App settings → "Environment"
2. Add variables:
   ```
   BACKEND_API_KEY=changeme123
   ALLOWED_ORIGINS=*
   CLASSIFY_API_URL=http://localhost:8000/classify
   ANALYZE_API_URL=http://localhost:8000/analyze
   HUGGINGFACE_API_KEY=<your-hf-token>
   ```
3. Click "Save"

### Step 5: Deploy
1. Click "Create App"
2. DigitalOcean builds and deploys (10-15 min)
3. Get live URL: `https://your-app-<hash>.ondigitalocean.app`

### Step 6: Add Custom Domain
1. App settings → "Domains"
2. Add your custom domain
3. Point DNS to DigitalOcean nameservers
4. SSL certificate auto-generated

## Auto-Deployment
Every push to `main` triggers deployment!

## Cost
- **Years 1-3**: FREE ($200 credit = ~40 months)
- **After**: $5/month (App Platform minimum)
- Custom domain: ~$12/year

## Why Not Used
- Requires credit: GitHub Student Pack benefits (not permanently free)
- User wanted credit card-free option

## To Activate
1. Claim $200 student credit
2. Follow steps 1-6 above
3. Deploy via App Platform
4. Add custom domain
