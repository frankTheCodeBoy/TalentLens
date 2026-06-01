"""Pytest configuration for test environment."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
import pytest


def is_backend_running(host='127.0.0.1', port=8000, timeout=1):
    """Check if backend is running on the given port."""
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def wait_for_backend(host='127.0.0.1', port=8000, timeout=30):
    """Wait for backend to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        if is_backend_running(host, port, timeout=1):
            return True
        time.sleep(0.5)
    return False


def is_ci_environment():
    """Check if running in CI/CD environment."""
    return any([
        os.getenv('CI'),
        os.getenv('GITHUB_ACTIONS'),
        os.getenv('GITLAB_CI'),
        'PYTEST_CURRENT_TEST' in os.environ and 'docker' in str(Path.cwd()).lower(),
    ])


@pytest.fixture(scope='session', autouse=True)
def auto_start_backend():
    """
    Auto-start FastAPI backend before tests if not already running.
    Only for local development (not CI).
    """
    # Skip in CI environments
    if is_ci_environment():
        return
    
    # Skip if backend already running
    if is_backend_running():
        print("✅ Backend already running on port 8000")
        return
    
    app_dir = Path(__file__).parent.parent
    
    print("\n🚀 Auto-starting FastAPI backend on port 8000...")
    
    try:
        # Start backend process
        backend_proc = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'api.main:app', 
             '--host', '127.0.0.1', '--port', '8000', '--log-level', 'error'],
            cwd=app_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        print(f"Backend starting (PID: {backend_proc.pid})...")
        
        # Wait for backend to be ready
        if not wait_for_backend():
            backend_proc.kill()
            print("❌ Backend failed to start after 30 seconds")
            return
        
        print("✅ Backend ready on http://127.0.0.1:8000\n")
        
        # Store for cleanup
        pytest.backend_proc = backend_proc
        
    except Exception as e:
        print(f"⚠️ Could not auto-start backend: {e}")
        print("Run manually: python -m uvicorn api.main:app --host 127.0.0.1 --port 8000\n")


def pytest_sessionfinish(session, exitstatus):
    """Clean up backend after tests."""
    if hasattr(pytest, 'backend_proc'):
        try:
            pytest.backend_proc.terminate()
            pytest.backend_proc.wait(timeout=5)
            print("\n🛑 Backend stopped")
        except Exception:
            try:
                pytest.backend_proc.kill()
            except Exception:
                pass


def pytest_collection_modifyitems(config, items):
    """
    Mark integration tests:
    - SKIP if backend not available
    - RUN if backend available
    """
    # In CI, always skip integration tests
    if is_ci_environment():
        integration_tests = {
            'test_root_without_api_key',
            'test_root_with_api_key',
            'test_classify_without_api_key',
            'test_classify_with_api_key',
            'test_resumes',
        }
        
        for item in items:
            if item.name in integration_tests:
                item.add_marker(pytest.mark.skip(reason="Skipped in CI"))
    else:
        # Locally, give backend time to start and check
        time.sleep(1)
        backend_available = is_backend_running()
        
        integration_tests = {
            'test_root_without_api_key',
            'test_root_with_api_key',
            'test_classify_without_api_key',
            'test_classify_with_api_key',
            'test_resumes',
        }
        
        for item in items:
            if item.name in integration_tests:
                if not backend_available:
                    item.add_marker(pytest.mark.skip(reason="Backend not running on port 8000"))
