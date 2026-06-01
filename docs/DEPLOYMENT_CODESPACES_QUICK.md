# 🚀 Deploy to GitHub Codespaces (FREE)

**Time:** 5 minutes  
**Cost:** FREE (60 hours/month included with GitHub Student Pack)  
**URL:** `https://<your-username>-<random>.github.dev`

## Step 1: Create Codespace
1. Go to your repo: https://github.com/frankTheCodeBoy/ai_doc_classifier
2. Click **Code** → **Codespaces** → **Create codespace on main**
3. Wait 2-3 minutes for environment to load

## Step 2: Start the Application
In the Codespaces terminal:

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your Hugging Face token:
# HUGGINGFACE_API_KEY=hf_your_token_here

# Start with Docker Compose
docker compose up -d
```

## Step 3: Access Your App
The Codespaces will automatically detect ports and show a notification:
- **Streamlit UI:** Click the port 8502 link
- **FastAPI API:** Click the port 8002 link, then add `/docs`

## Step 4: Share Your Live Link
Your Codespace URL format:
```
https://username-projectname-randomcode.github.dev:8502
```

## Step 5: Keep Codespace Running
- Codespace runs 24/7 while active
- Auto-pauses after 30 min of inactivity (doesn't count toward 60h limit)
- Manually stop when not using to save hours

## Troubleshooting

### Ports not showing?
```bash
docker compose ps
```

### Backend not responding?
```bash
docker compose logs api
```

### Restart everything
```bash
docker compose down
docker compose up -d
```

---

**Next:** Set up custom domain with name.com (see DOMAIN_SETUP.md)
