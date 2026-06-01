import os
import logging
from typing import Optional
import requests

logger = logging.getLogger(__name__)

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"


def summarize_resume_with_hf(text: str) -> Optional[str]:
    """
    Summarize resume text using Hugging Face API (free tier).
    Falls back to local summarization if API fails or key is missing.
    """
    if not HUGGINGFACE_API_KEY:
        logger.warning("HUGGINGFACE_API_KEY not set, skipping HF summarization")
        return None

    try:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        # Truncate text to 1024 chars to stay within API limits
        truncated_text = text[:1024]
        
        payload = {
            "inputs": truncated_text,
            "parameters": {
                "max_length": 150,
                "min_length": 50,
            }
        }
        
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            summary = result[0].get("summary_text", "")
            if summary:
                return summary
                
    except requests.exceptions.RequestException as exc:
        logger.warning("Hugging Face API call failed: %s", exc)
    except (KeyError, IndexError, ValueError) as exc:
        logger.warning("Failed to parse Hugging Face response: %s", exc)
    
    return None
