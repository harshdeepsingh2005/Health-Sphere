"""
HealthSphere AI — AI Client
============================

Uses Google Gemini when GEMINI_API_KEY is set, otherwise returns None
gracefully so views can fall back to demo/cached data without crashing.

Public API:
  generate_text(prompt, system_instruction=None, model_name=None, history=None) -> str | None
  is_available() -> bool
  quota_status() -> dict
"""

import logging
import os

logger = logging.getLogger(__name__)

# ── Runtime cache ──────────────────────────────────────────────────────────────
_available: bool | None = None   # None = not yet probed
_error_message: str = ''


def _get_api_key() -> str:
    try:
        from django.conf import settings
        return getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
    except Exception:
        return os.environ.get('GEMINI_API_KEY', '')


def _get_model() -> str:
    try:
        from django.conf import settings
        return (
            getattr(settings, 'GEMINI_MODEL', None)
            or os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')
        )
    except Exception:
        return os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')


def _probe() -> bool:
    """Probe Gemini availability once per process."""
    global _available, _error_message
    if _available is not None:
        return _available

    api_key = _get_api_key()
    if not api_key:
        _available = False
        _error_message = 'GEMINI_API_KEY not set — AI features disabled.'
        logger.warning(_error_message)
        return False

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _available = True
        logger.info(f'Gemini AI ready. Model: {_get_model()}')
    except Exception as exc:
        _available = False
        _error_message = str(exc)
        logger.warning(f'Gemini init failed: {exc}')

    return _available


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_text(
    prompt: str,
    system_instruction: str = None,
    model_name: str = None,
    history: list = None,
) -> str | None:
    """
    Send a prompt to Gemini and return the text response.
    Returns None if the API key is missing or a network error occurs.
    """
    if not _probe():
        return None

    import google.generativeai as genai

    model = model_name or _get_model()

    try:
        generation_config = {'temperature': 0.7, 'max_output_tokens': 1024}

        # Build conversation history for multi-turn if provided
        history_msgs = []
        for h in (history or []):
            role = h.get('role', 'user')
            if role == 'ai':
                role = 'model'
            content = h.get('text') or h.get('content', '')
            if content:
                history_msgs.append({'role': role, 'parts': [content]})

        m = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )

        if history_msgs:
            chat = m.start_chat(history=history_msgs)
            response = chat.send_message(prompt)
        else:
            response = m.generate_content(prompt)

        return response.text

    except Exception as exc:
        logger.error(f'Gemini generation error (model={model}): {exc}')
        return None


def is_available() -> bool:
    """Return True if Gemini is configured and reachable."""
    return _probe()


def quota_status() -> dict:
    """Return a status dict for use by views and templates."""
    api_key = _get_api_key()
    available = _probe()
    return {
        'configured': bool(api_key),
        'quota_exhausted': False,
        'available': available,
        'model': _get_model(),
        'error': _error_message if not available else '',
    }
