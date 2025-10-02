from __future__ import annotations
import importlib
import sys
from fastapi.testclient import TestClient


def _load_app():
    if "app.main" in sys.modules:
        app_module = sys.modules["app.main"]
        app_module = importlib.reload(app_module)
    else:
        app_module = importlib.import_module("app.main")
    return getattr(app_module, "app")


def test_cors_in_prod_respects_whitelist(monkeypatch):
    # Arrange: emulate prod + single allowed origin
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("CORS_ORIGINS", "https://allowed.example")

    app = _load_app()
    client = TestClient(app)

    # Allowed origin reflected
    r = client.options(
        "/api/v1/healthz",
        headers={
            "Origin": "https://allowed.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r.headers.get("access-control-allow-origin") == "https://allowed.example"

    # Disallowed origin is not reflected
    r2 = client.options(
        "/api/v1/healthz",
        headers={
            "Origin": "https://blocked.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r2.headers.get("access-control-allow-origin") in (None, "null")
