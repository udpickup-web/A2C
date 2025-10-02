from fastapi.testclient import TestClient
from app.main import app

def test_register_and_export():
    views = {
      "views": [
        {
          "id": "front",
          "bbox_px": [0,0,100,100],
          "angle_deg": 0.0,
          "sketch": {
            "outer_polygon_px": [[0,0],[100,0],[100,50],[0,50]],
            "holes_px": [{"center_px":[50,25], "r_px": 5.0}],
            "solved": {"outer": True, "holes": True, "slots": True, "arcs": True}
          }
        }
      ]
    }
    preflight = {"standard":"ISO","projection":"first","units":"mm","scale":"1:1","page":{"w_px":2480,"h_px":3508}}
    with TestClient(app) as client:
        r = client.post("/api/v1/register", json={"views": views, "preflight": preflight})
        assert r.status_code == 200
        j = r.json()
        assert "views_anchors" in j and "front" in j["views_anchors"]

        exp = client.post("/api/v1/export", json={
            "features": {"features":[{"type":"base_extrude","mode":"extrude","depth_mm":10}]},
            "plan": {"order":["front"], "units":"mm"}
        })
        assert exp.status_code == 200
        ej = exp.json()
        for key in ("step_url","stl_url","glb_url","export_report"):
            assert key in ej
