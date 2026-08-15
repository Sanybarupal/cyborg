from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_backend_has_health_and_status_routes():
    source = (ROOT / "server.py").read_text(encoding="utf-8")
    assert '@app.get("/health")' in source
    assert '@app.get("/api/system-status")' in source
    assert 'except Exception as exc:' in source


def test_voice_requires_jarvis_wake_word():
    source = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "WAKE_WORD" in source
    assert "voiceArmed" in source
    assert "JARVIS" in source


def test_frontend_escapes_telemetry_values():
    source = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "escapeHtml" in source
    assert "escapeHtml(a.action)" in source
    assert "escapeHtml(a.time)" in source
