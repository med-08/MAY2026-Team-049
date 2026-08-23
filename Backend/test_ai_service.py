import io
import json
import urllib.error

import pytest

from ai_service import (
    AIConfigError,
    AIResponseError,
    AIServiceError,
    generate_text,
)


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


def test_generate_text_keeps_key_out_of_url(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-secret-key")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        body = {"choices": [{"message": {"content": "Ready"}}]}
        return FakeResponse(json.dumps(body).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    assert generate_text("Hello", timeout=4) == "Ready"
    assert "test-secret-key" not in captured["request"].full_url
    assert captured["request"].get_header("Authorization") == "Bearer test-secret-key"
    assert captured["timeout"] == 4


def test_generate_text_requires_backend_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(AIConfigError, match="not configured"):
        generate_text("Hello")


def test_generate_text_handles_provider_http_error(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-secret-key")
    error = urllib.error.HTTPError(
        "https://provider.invalid",
        429,
        "Too Many Requests",
        {},
        io.BytesIO(json.dumps({"error": {"message": "Quota exceeded"}}).encode()),
    )
    monkeypatch.setattr("urllib.request.urlopen", lambda *_args, **_kwargs: (_ for _ in ()).throw(error))

    with pytest.raises(AIServiceError, match="HTTP 429: Quota exceeded") as exc_info:
        generate_text("Hello")
    assert "test-secret-key" not in str(exc_info.value)


def test_generate_text_handles_timeout(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-secret-key")
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError()),
    )

    with pytest.raises(AIServiceError, match="timed out"):
        generate_text("Hello")


def test_generate_text_rejects_invalid_json(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-secret-key")
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(b"not-json"),
    )

    with pytest.raises(AIResponseError, match="invalid JSON"):
        generate_text("Hello")


def test_generate_text_rejects_empty_response(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-secret-key")
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_args, **_kwargs: FakeResponse(b'{"choices": []}'),
    )

    with pytest.raises(AIResponseError, match="empty response"):
        generate_text("Hello")
