import json
import os
import urllib.error
import urllib.request


class AIConfigError(RuntimeError):
    pass


class AIServiceError(RuntimeError):
    pass


class AIResponseError(RuntimeError):
    pass


def _api_key():
    return os.environ.get("OPENROUTER_API_KEY")


def generate_text(prompt, *, timeout=30, response_mime_type=None):
    """Generate text through OpenRouter without exposing provider keys to clients."""
    key = _api_key()
    if not key:
        raise AIConfigError(
            "AI service is not configured. Set OPENROUTER_API_KEY on the backend."
        )

    model = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
    }
    # Not forwarded as response_format: OpenAI-style json_object mode requires a
    # top-level JSON object, but the quiz-generation prompt asks for a JSON
    # array, so forcing it here would break existing parsing instead of
    # helping it. The prompt's own JSON instructions already do the work.

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        try:
            provider_message = json.loads(details).get("error", {}).get("message")
        except (json.JSONDecodeError, AttributeError):
            provider_message = None
        message = f"AI provider returned HTTP {exc.code}"
        if provider_message:
            message = f"{message}: {provider_message}"
        raise AIServiceError(message) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise AIServiceError("AI provider request failed or timed out.") from exc
    except json.JSONDecodeError as exc:
        raise AIResponseError("AI provider returned invalid JSON.") from exc

    choices = data.get("choices") or []
    text = (
        (choices[0].get("message") or {}).get("content", "")
        if choices
        else ""
    ).strip()
    if not text:
        raise AIResponseError("AI provider returned an empty response.")
    return text


def ai_error_response(jsonify, message, status):
    return jsonify({"success": False, "status": "error", "message": message}), status
