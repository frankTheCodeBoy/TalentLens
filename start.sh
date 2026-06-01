#!/bin/bash
echo "🚀 Starting AI Resume Classifier..."
cd /app
export PYTHONPATH=/app
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
streamlit run ui/app.py --server.port 8502 --server.address 0.0.0.0
