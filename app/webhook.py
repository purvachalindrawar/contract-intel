"""
Simple webhook emitter. Used to POST JSON payloads to a provided URL.
Runs in background via FastAPI BackgroundTasks.
"""

import requests
from typing import Dict

def emit_event(url: str, payload: Dict, timeout: int = 5) -> Dict:
    """
    POST the payload to the webhook URL. Return a small status dict.
    This function should be executed in the background (non-blocking).
    """
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        return {"status_code": resp.status_code, "text": resp.text[:100]}
    except Exception as e:
        return {"error": str(e)}
