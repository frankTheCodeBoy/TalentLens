# Deploy with GitHub Codespaces (100% FREE)

## Why GitHub Codespaces?
- ✅ 60 hours/month FREE (GitHub Student Pack)
- ✅ Full Docker support
- ✅ Run your app 24/7
- ✅ No credit card needed
- ✅ Built-in terminal access
- ✅ VS Code in browser
- ✅ Public URLs automatically generated

## Setup (3 steps)

### Step 1: Create Codespace
1. Go to: https://github.com/frankTheCodeBoy/ai_doc_classifier
2. Click green "Code" button
3. Click "Codespaces" tab
4. Click "Create codespace on main"
5. Wait for container to start (~2 minutes)

### Step 2: Start Your App
In the Codespaces terminal:
```bash
docker compose up -d
```

Or manually:
```bash
# Start backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Start frontend
streamlit run ui/app.py --server.port=8501 --server.headless=true
```

### Step 3: Access Your App
Codespaces auto-generates public URLs:
- **Streamlit UI**: Click the notification or go to "Ports" tab → click 8501
- **API Docs**: Click 8000 port link
- **Public URLs**: `https://your-codespace-name-xxxx.github.dev:8501`

## Environment Variables
1. In Codespaces terminal, create `.env`:
```bash
cat > .env << EOF
BACKEND_API_KEY=changeme123
ALLOWED_ORIGINS=*
CLASSIFY_API_URL=http://localhost:8000/classify
ANALYZE_API_URL=http://localhost:8000/analyze
HUGGINGFACE_API_KEY=<your-hf-token>
EOF
```

2. Load environment:
```bash
export $(cat .env | xargs)
```

## Run Tests
```bash
pytest -v
```

## Keep App Running
Codespaces auto-suspend after inactivity. To keep running:

**Option 1: Disable auto-suspend (free)**
```bash
gh codespace update --codespace <name> --idle-timeout 30m
```

**Option 2: Use GitHub Actions to wake it**
Create `.github/workflows/keep-alive.yml`:
```yaml
name: Keep Codespace Alive
on:
  schedule:
    - cron: '0 * * * *'  # Every hour

jobs:
  keep-alive:
    runs-on: ubuntu-latest
    steps:
      - name: Wake up Codespace
        run: echo "Keeping codespace alive"
```

## Cost Breakdown
- **60 hours/month**: Completely FREE
- Enough for: 2.5 hours daily always-on
- Student Pack: Perpetually free while you're a student

## Limitations
- Max 4 Codespaces at once
- 60 hours/month (can request more)
- Disconnects after 30 min inactivity (can extend)

## Advantages Over Others
- No separate hosting service
- Everything in GitHub
- Full development environment
- Can push updates directly
- 100% free forever (as student)

## To Deploy Updates
1. Make changes locally
2. Push to GitHub (`git push origin main`)
3. In Codespaces: `git pull`
4. Restart app: `docker compose down && docker compose up -d`

## Custom Domain (Optional)
Use ngrok for tunnel to custom domain:
```bash
npm install -g ngrok
ngrok http 8501
```

---

**You're ready to go!**

1. Go to your GitHub repo
2. Click "Code" → "Codespaces" → "Create"
3. Wait for container
4. Run: `docker compose up -d`
5. Click port 8501 link
6. Your app is live!

No credit card. No payment. Ever.
