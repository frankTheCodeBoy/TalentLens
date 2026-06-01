# 🚀 deploy.sh - One Command Deployment

## What It Does

Single command that:
✅ Verifies GitHub Secrets are set  
✅ Exports all environment variables (including HUGGINGFACE_API_KEY)  
✅ Installs Python dependencies  
✅ Builds Docker images  
✅ Starts FastAPI + Streamlit  
✅ Waits for services to be ready  
✅ Shows you how to access the app  

## Usage

### In Codespaces (After clicking the button)
```bash
bash deploy.sh
```

### Locally
```bash
# Make sure you have GitHub Secrets set up, then:
bash deploy.sh

# Or use environment variables:
export HUGGINGFACE_API_KEY="hf_your_token"
bash deploy.sh
```

## What Happens

```
🚀 AI Resume Classifier - Automated Deployment Script
✅ Environment: GitHub Codespaces
🔐 Step 1: Loading GitHub Secrets...
✅ HUGGINGFACE_API_KEY loaded
📤 Step 2: Exporting environment variables...
✅ Environment variables exported
📦 Step 3: Installing dependencies...
✅ Dependencies installed
🐳 Step 4: Building Docker images...
✅ Docker images built
🚀 Step 5: Starting services...
✅ Services launched
⏳ Step 6: Waiting for services to be ready...
📊 Step 7: Checking service status...
✅ DEPLOYMENT COMPLETE!
```

## After Deployment

**In Codespaces:**
1. Look at PORTS tab (bottom of screen)
2. Click the link for port 8502
3. Your app opens! 🎉

**Locally:**
- Streamlit UI: http://localhost:8502
- API Docs: http://localhost:8002/docs

## Troubleshooting

**"HUGGINGFACE_API_KEY not found"**
→ Add it to GitHub Secrets first

**"Docker not installed"**
→ Install Docker Desktop from docker.com

**Services won't start**
→ Check: `docker compose logs`

**Need to restart**
→ Run: `docker compose down` then `bash deploy.sh` again

---

That's it! One script to rule them all. 🧠
