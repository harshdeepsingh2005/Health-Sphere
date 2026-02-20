"""
HealthSphere AI — Ollama Client
================================

Drop-in replacement for the Gemini client that uses a local/cloud Ollama model.
Keeps the same public interface so all services (risk_service, report_explainer,
journey_service, views) continue to work without any changes.

Default model: gpt-oss:120b-cloud  (~1.3 s response, very high quality)
Override via OLLAMA_MODEL in .env, or set OLLAMA_HOST for a remote server.

Public API (identical to gemini_client.py):
  generate_text(prompt, system_instruction=None, model_name=None) -> str | None
  is_available() -> bool
  quota_status() -> dict
"""

import logging
import os

logger = logging.getLogger(__name__)

# ── Default model (overridable from settings / .env) ──────────────────────────
_DEFAULT_MODEL = 'gpt-oss:120b-cloud'

# ── Runtime state ─────────────────────────────────────────────────────────────
_ollama_available: bool | None = None   # None = not yet probed
_error_message: str = ''


def _get_model() -> str:
    """Return the model name from settings / env, falling back to default."""
    from django.conf import settings
    return (
        getattr(settings, 'OLLAMA_MODEL', None)
        or os.environ.get('OLLAMA_MODEL', _DEFAULT_MODEL)
    )


def _probe() -> bool:
    """
    Probe Ollama connectivity once per process.
    Sets _ollama_available True/False and logs the outcome.
    """
    global _ollama_available, _error_message
    if _ollama_available is not None:
        return _ollama_available

    try:
        from ollama import list as ollama_list
        ollama_list()   # lightweight health-check (just fetches model list)
        _ollama_available = True
        logger.info(f"Ollama is reachable. Using model: {_get_model()}")
    except Exception as exc:
        _ollama_available = False
        _error_message = str(exc)
        logger.warning(f"Ollama not reachable: {exc} — AI features will use fallback data.")

    return _ollama_available


# ── Public API ────────────────────────────────────────────────────────────────

def generate_text(
    prompt: str,
    system_instruction: str = None,
    model_name: str = None,
    history: list = None,
) -> str | None:
    """
    Send a prompt to Ollama and return the text response.

    Args:
        prompt:             The user message.
        system_instruction: Optional system prompt prepended to conversation.
        model_name:         Override the configured model for this call only.
        history:            Optional list of prior messages
                            [{'role': 'user'|'assistant'|'ai', 'text': '...'}, ...]

    Returns:
        The model's text response, or None if Ollama is unavailable / errors.
    """
    if not _probe():
        return None

    model = model_name or _get_model()

    # Build the messages list
    messages = []

    if system_instruction:
        messages.append({'role': 'system', 'content': system_instruction})

    # Replay conversation history (supports both 'text' and 'content' keys)
    for h in (history or []):
        role = h.get('role', 'user')
        if role == 'ai':
            role = 'assistant'
        content = h.get('text') or h.get('content', '')
        if content:
            messages.append({'role': role, 'content': content})

    # Current user turn
    messages.append({'role': 'user', 'content': prompt})

    try:
        from ollama import chat
        response = chat(model=model, messages=messages)
        return response.message.content

    except Exception as exc:
        logger.error(f"Ollama generation error (model={model}): {exc}")
        return None


def is_available() -> bool:
    """Return True if Ollama is reachable and ready."""
    return _probe()


def quota_status() -> dict:
    """
    Return status dict compatible with the old Gemini quota_status().
    'configured'      — always True (Ollama needs no API key)
    'quota_exhausted' — always False (Ollama has no quota)
    'available'       — True if Ollama daemon is reachable
    """
    available = _probe()
    return {
        'configured': True,           # no API key needed
        'quota_exhausted': False,     # no quota concept
        'available': available,
        'model': _get_model(),
        'error': _error_message if not available else '',
    }
