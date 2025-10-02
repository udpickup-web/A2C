from fastapi.testclient import TestClient
from app.main import app


def test_preflight_ok():
    payload = {
        "standard": "ISO",
        "projection": "first",
        "units": "mm",
        "scale": "1:1",
        "page": {"w_px": 1000, "h_px": 1000},
    }
    with TestClient(app) as client:
        r = client.post("/api/v1/preflight", json=payload)
        assert r.status_code == 200
        j = r.json()
        assert j["normalized"]["scale_ratio"] == 1.0
        assert "preflight_id" in j


def test_preflight_extra_field_is_rejected():
    payload = {
        "standard": "ISO",
        "projection": "first",
        "units": "mm",
        "scale": "1:1",
        "page": {"w_px": 1000, "h_px": 1000},
        "extra": "nope",
    }
    with TestClient(app) as client:
        r = client.post("/api/v1/preflight", json=payload)
        assert r.status_code == 422
        assert "error" in r.json()
        assert r.json()["error"]["code"] == 422
