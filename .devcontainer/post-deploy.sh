#!/bin/bash
# Auto-launch browser to Streamlit app after deployment
# This runs after deploy.sh completes

set -e

# Wait for Streamlit to be fully ready
echo "⏳ Waiting for Streamlit to be fully ready..."
sleep 10

# Check if running in Codespaces
if [ -n "$CODESPACES" ]; then
    # Get the Codespaces URL
    CODESPACE_NAME=$(echo $CODESPACE_NAME)
    GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN=${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-githubpreview.dev}
    
    # Construct the direct Streamlit URL
    APP_URL="https://${CODESPACE_NAME}-8502.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✅ APP IS LIVE - DIRECT LINK BELOW                       ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎨 Your AI Resume Classifier is ready!"
    echo ""
    echo "📍 Direct link (open in browser):"
    echo "   $APP_URL"
    echo ""
    echo "   👆 Click the link above or copy-paste into browser"
    echo ""
    echo "📡 API Documentation:"
    echo "   https://${CODESPACE_NAME}-8002.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/docs"
    echo ""
else
    echo "Streamlit UI:   http://localhost:8502"
    echo "API Docs:       http://localhost:8002/docs"
fi
