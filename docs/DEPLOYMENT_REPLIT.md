# Deploy to Replit (100% Free, No Credit Card)

## Why Replit?
- ✅ Completely free
- ✅ No credit card needed ever
- ✅ GitHub Student Pack benefit
- ✅ Works with Docker
- ✅ 1GB storage free
- ✅ Automatic deployments

## Deployment Steps

### Step 1: Create Replit Account
1. Go to https://replit.com
2. Click "Sign up"
3. Choose "Sign up with GitHub"
4. Authorize Replit

### Step 2: Import Repository
1. Click "+ Create Repl"
2. Select "Import from GitHub"
3. Paste: `https://github.com/frankTheCodeBoy/ai_doc_classifier`
4. Click "Import from GitHub"

### Step 3: Configure Environment
1. Create `.env` file in Replit:
   ```
   BACKEND_API_KEY=changeme123
   ALLOWED_ORIGINS=*
   CLASSIFY_API_URL=http://localhost:8000/classify
   ANALYZE_API_URL=http://localhost:8000/analyze
   HUGGINGFACE_API_KEY=<your-hf-token>
   ```

2. Click "Secrets" (lock icon)
3. Add environment variables there

### Step 4: Run the Project
1. Click "Run" button
2. Replit builds Docker image
3. App starts automatically
4. You get a live URL like: `https://resumeclassifier.replit.dev`

### Step 5: Enable Always-On (Optional, free)
1. Click "Hosting"
2. Toggle "Always On"
3. Keep your app running 24/7

### Step 6: Custom Domain
1. Go to "Hosting"
2. Click "Domains"
3. Add your custom domain
4. Point DNS to Replit servers

## Access Your App
- **Streamlit UI:** `https://your-replit-domain:8501`
- **API Docs:** `https://your-replit-domain:8000/docs`

## Auto-Deployment
Push to GitHub main branch → Replit auto-deploys

## Limits (Free Tier)
- Storage: 1GB
- Memory: 512MB RAM
- Bandwidth: Generous limits
- CPU: Shared

## Cost
**Forever free** - No credit card needed, no ads, no limitations

---

**Next Steps:**
1. Go to https://replit.com
2. Sign up with GitHub
3. Click "Import from GitHub"
4. Paste your repo URL
5. Add environment variables
6. Click "Run"
7. Done!
