#!/bin/bash
# Adaptive Deployment Script for AI Resume Classifier
# Works with or without Docker, includes disk space check
# Usage: bash deploy.sh

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🚀 AI Resume Classifier - Adaptive Deployment Script      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# STEP 0: Disk Space Check
# ============================================================================
echo "💾 Step 0: Checking disk space..."
FREE=$(df -h /vscode | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$FREE" -ge 90 ]; then
    echo "❌ ERROR: Disk usage above 90%! Please free space before deploying."
    exit 1
elif [ "$FREE" -ge 85 ]; then
    echo "⚠️ WARNING: Disk usage above 85%. Builds may fail if space runs out."
else
    echo "✅ Disk space sufficient"
fi
echo ""

# ============================================================================
# STEP 1: Environment Check
# ============================================================================
if [ -n "$CODESPACES" ]; then
    echo "✅ Environment: GitHub Codespaces"
else
    echo "📌 Environment: Local Machine"
fi
echo ""

# ============================================================================
# STEP 2: Verify and Export GitHub Secrets
# ============================================================================
echo "🔐 Step 1: Loading GitHub Secrets..."
if [ -z "$HUGGINGFACE_API_KEY" ]; then
    echo "❌ ERROR: HUGGINGFACE_API_KEY not found!"
    exit 1
fi
export HUGGINGFACE_API_KEY="${HUGGINGFACE_API_KEY}"
export BACKEND_API_KEY="codespaces-secure-key"
export ALLOWED_ORIGINS="https://*.githubpreview.dev,http://localhost:8501,http://127.0.0.1:8501"
export CLASSIFY_API_URL="http://localhost:8000/classify"
export ANALYZE_API_URL="http://localhost:8000/analyze"
echo "✅ Secrets exported"
echo ""

# ============================================================================
# STEP 3: Install Dependencies
# ============================================================================
echo "📦 Step 2: Installing dependencies..."
if command -v pip &> /dev/null; then
    pip install --no-cache-dir -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️ pip not found, skipping"
fi
echo ""

# ============================================================================
# STEP 4: Deployment Mode
# ============================================================================
echo "🚀 Step 3: Starting services..."
if command -v docker &> /dev/null; then
    echo "🐳 Docker detected. Building images..."
    docker compose build --no-cache
    docker compose up -d
    echo "✅ Services launched via Docker"
    docker compose ps
else
    echo "⚠️ Docker not found. Running directly..."
    export PYTHONPATH=/workspaces/ai_doc_classifier
    uvicorn api.main:app --host 0.0.0.0 --port 8000 &
    streamlit run ui/app.py --server.port 8502 --server.address 0.0.0.0
fi
echo ""

# ============================================================================
# STEP 5: Success Message
# ============================================================================
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ DEPLOYMENT COMPLETE!                                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🎨 Your AI Resume Classifier is ready!"
echo "📍 Access via PORTS tab (Codespaces) or localhost"
