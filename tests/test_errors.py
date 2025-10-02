from fastapi.testclient import TestClient
from app.main import app

def test_empty_json_400():
    with TestClient(app) as client:
        r = client.post("/api/v1/preflight", data="", headers={"Content-Type":"application/json"})
        assert r.status_code == 400
        j = r.json()
        assert j["error"]["code"] == 400
        assert "Empty JSON" in j["error"]["message"]

def test_missing_fields_422():
    with TestClient(app) as client:
        r = client.post("/api/v1/preflight", json={"standard":"ISO"})
        assert r.status_code == 422
        j = r.json()
        assert j["error"]["code"] == 422
