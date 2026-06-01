#!/bin/bash
echo "🚀 Starting TalentLens (Streamlit-only)..."
cd /app
export PYTHONPATH=/app
streamlit run app.py --server.port=7860 --server.address=0.0.0.0

