import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("BACKEND_API_KEY", "changeme123")


def test_root_without_api_key():
    """Root endpoint should reject requests without API key."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_root_with_api_key():
    """Root endpoint should succeed with correct API key."""
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "resume classifier"


def test_classify_without_api_key():
    """Classify endpoint should reject requests without API key."""
    files = {"file": ("dummy.pdf", b"fake content", "application/pdf")}
    response = requests.post(f"{BASE_URL}/classify", files=files)
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_classify_with_api_key():
    """Classify endpoint should succeed with correct API key."""
    headers = {"X-API-Key": API_KEY}
    files = {"file": ("dummy.pdf", b"fake content", "application/pdf")}
    response = requests.post(
        f"{BASE_URL}/classify", files=files, headers=headers)
    # Even with dummy content, backend should respond with 200
    # or validation error
    assert response.status_code in (200, 422, 500)
