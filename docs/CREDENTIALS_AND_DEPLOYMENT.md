# 🚀 Production Deployment Guide

## How Credentials Work in Production

### Local Development (Your Computer)
```
.env file (your computer, never committed)
    ↓
python/docker reads .env
    ↓
App works with your real HF token
```

### GitHub Codespaces (Free Cloud)
```
GitHub Secrets (secure storage in GitHub)
    ↓
Codespaces environment variables (automatically injected)
    ↓
.devcontainer/devcontainer.json reads secrets
    ↓
App works with your real HF token
```

### Docker/Production (Any Server)
```
Docker run with -e flags (or environment file)
    ↓
docker-compose.yml reads from .env or -e variables
    ↓
App works with credentials
```

---

## Setup Steps for Production

### Step 1: Add GitHub Secrets (ONE TIME)

1. Go to: https://github.com/frankTheCodeBoy/ai_doc_classifier
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Name | Value |
|------|-------|
| `HUGGINGFACE_API_KEY` | Your real HF token (hf_...) |
| `BACKEND_API_KEY` | Your secure API key (not "changeme123") |

### Step 2: Deploy to Codespaces

1. Click: **[Open in GitHub Codespaces](https://codespaces.new/frankTheCodeBoy/ai_doc_classifier?quickstart=1)**
2. Wait for Codespaces to load
3. In terminal:
```bash
docker compose up -d
```
4. Click port 8502 link
5. **✅ App is live with your credentials!**

### Step 3: Verify Credentials Are Loaded

```bash
# In Codespaces terminal:
docker compose logs
```

You should see:
```
api_1  | Loaded HUGGINGFACE_API_KEY from environment ✅
api_1  | Connected to HuggingFace API ✅
```

---

## How It Works Behind the Scenes

### `.devcontainer/devcontainer.json`
- Tells Codespaces to create the environment
- Automatically injects GitHub Secrets as environment variables
- Sets up Docker, ports, and forwarding

### `docker-compose.yml`
- Reads `HUGGINGFACE_API_KEY` from environment
- Passes it to the container
- App can access it via `os.getenv("HUGGINGFACE_API_KEY")`

### `api/main.py`
```python
load_dotenv()  # Loads from .env (local) or environment (production)
API_KEY = os.getenv("BACKEND_API_KEY", "changeme123")
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")  # From GitHub Secrets in production
```

---

## Security Checklist ✅

- ✅ Real credentials in GitHub Secrets (not in code)
- ✅ `.env` in `.gitignore` (never committed)
- ✅ `.devcontainer.json` auto-injects secrets in Codespaces
- ✅ Production has different API key than development
- ✅ Credentials passed as environment variables (not files)

---

## Troubleshooting

### App says "HUGGINGFACE_API_KEY not found"

**Solution:** You haven't set the GitHub Secret yet.

```bash
# Add to GitHub Secrets:
HUGGINGFACE_API_KEY=hf_your_real_token
```

Then redeploy Codespaces.

### "Connection to HuggingFace failed"

**Possible causes:**
1. Token is invalid/expired
2. Token doesn't have proper permissions
3. Network is blocked

**Fix:**
```bash
# Get a new token:
# https://huggingface.co/settings/tokens

# Update GitHub Secret:
# Settings → Secrets → HUGGINGFACE_API_KEY → Update value
```

### Want to test locally?

```bash
# Create .env in project root:
HUGGINGFACE_API_KEY=hf_your_real_token
BACKEND_API_KEY=test123

# Run:
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000

# Or:
docker compose up -d
```

---

## Summary

| Environment | Credentials Source | Status |
|-------------|-------------------|--------|
| **Local** | `.env` file | ✅ Ready |
| **Codespaces** | GitHub Secrets → env vars | ✅ Ready (after Step 1) |
| **Production** | Environment variables | ✅ Ready (any server) |

**Next:** Add your HF token to GitHub Secrets (Step 1 above), then deploy!
