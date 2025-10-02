from __future__ import annotations

import uuid
from typing import Dict

from fastapi.testclient import TestClient

# Test assumes app.main:app exists and includes APIRouter with prefix '/api/v1'
try:
    from app.main import app  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError("tests expect FastAPI app at app.main:app") from e

client = TestClient(app)


def _auth_headers() -> Dict[str, str]:
    # In dev, token is optional; in prod required. Tests always send it.
    return {"Authorization": "Bearer demo"}


def test_export_by_model_id_happy_path(tmp_path, monkeypatch):
    # Arrange: create fake artifacts for a known UUID
    model_id = uuid.uuid4()
    art_dir = tmp_path / "artifacts" / str(model_id)
    art_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("step", "stl", "glb"):
        (art_dir / f"model.{ext}").write_bytes(b"dummy")

    # Patch ARTIFACTS_DIR used by the app to our tmp dir
    import app.main as main_mod

    monkeypatch.setattr(main_mod, "ARTIFACTS_DIR", str(tmp_path / "artifacts"), raising=True)

    # Recreate static mount? Not required for TestClient since we only return URLs.
    # Act
    resp = client.post(
        "/api/v1/export",
        headers=_auth_headers(),
        json={"model_id": str(model_id)},
    )

    # Assert
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["step_url"].endswith(f"/artifacts/{model_id}/model.step")
    assert data["stl_url"].endswith(f"/artifacts/{model_id}/model.stl")
    assert data["glb_url"].endswith(f"/artifacts/{model_id}/model.glb")
    assert data["export_report"]["exists"] == {"step": True, "stl": True, "glb": True}


def test_export_rejects_mixed_inputs():
    resp = client.post(
        "/api/v1/export",
        headers=_auth_headers(),
        json={"model_id": str(uuid.uuid4()), "features": {}, "plan": {}},
    )
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body or "detail" in body  # depending on global error wrapper


def test_export_requires_proper_shape():
    # Missing both branches
    resp = client.post("/api/v1/export", headers=_auth_headers(), json={"foo": "bar"})
    assert resp.status_code == 400

    # Bad UUID
    resp2 = client.post("/api/v1/export", headers=_auth_headers(), json={"model_id": "not-a-uuid"})
    assert resp2.status_code == 422

    # features/plan must be objects
    resp3 = client.post(
        "/api/v1/export", headers=_auth_headers(), json={"features": [], "plan": {}}
    )
    assert resp3.status_code in (400, 422)
