# app/routers/export.py
"""
Replacement router for /export to support alternative input via { "model_id": "<uuid>" }.
Pydantic v2, FastAPI. Follows unified error contract from the project (handled globally).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, HTTPException, status

router = APIRouter(prefix="/api/v1", tags=["export"])

ARTIFACTS_DIR = Path("artifacts")  # relative to /app working dir in Dockerfile


def _artifact_urls(model_id: UUID) -> Dict[str, str]:
    # Public URLs are served by the same app as static files (mapped volume ./artifacts:/app/artifacts).
    base = f"/artifacts/{model_id}"
    return {
        "step_url": f"{base}/model.step",
        "stl_url": f"{base}/model.stl",
        "glb_url": f"{base}/model.glb",
    }


def _exists_report(model_id: UUID) -> Dict[str, bool]:
    base = ARTIFACTS_DIR / str(model_id)
    return {
        "step": (base / "model.step").exists(),
        "stl": (base / "model.stl").exists(),
        "glb": (base / "model.glb").exists(),
    }


@router.post("/export")
def export_endpoint(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Accepts either:
      A) {"model_id": "<uuid>"}  → resolves artifacts/<uuid>/model.{step,stl,glb}
      B) {"features": {...}, "model_plan": {...}} → returns stubbed URLs with a generated model_id

    Returns:
      { "step_url": str, "stl_url": str, "glb_url": str, "export_report": {...} }
    """
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Body must be an object."},
        )

    has_model_id = "model_id" in payload
    has_features = "features" in payload
    has_plan = "model_plan" in payload

    # Guard against mixed inputs to keep the contract simple and deterministic
    if has_model_id and (has_features or has_plan):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Provide either 'model_id' OR ('features' + 'model_plan'), not both."
            },
        )

    # Path A: by model_id
    if has_model_id:
        try:
            model_id = UUID(str(payload["model_id"]))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Field 'model_id' must be a valid UUID."},
            )
        urls = _artifact_urls(model_id)
        exists = _exists_report(model_id)
        return {
            **urls,
            "export_report": {
                "source": "by_model_id",
                "resolver": "filesystem",
                "model_id": str(model_id),
                "exists": exists,
            },
        }

    # Path B: by features + plan (stub)
    if has_features and has_plan:
        # Validate minimal structure (project uses pydantic v2 globally; here we keep light checks)
        if not isinstance(payload["features"], dict) or not isinstance(payload["model_plan"], dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "'features' and 'model_plan' must be objects."},
            )
        # Generate a deterministic-like id for this export run (stub). In real pipeline id comes from builder.
        model_id = uuid4()
        urls = _artifact_urls(model_id)
        return {
            **urls,
            "export_report": {
                "source": "by_features_and_plan",
                "resolver": "pipeline_stub",
                "model_id": str(model_id),
                "notes": "This is a stub response; actual files may not exist until the builder runs.",
            },
        }

    # If neither branch matched — it's a contract error
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "message": "Body must contain either 'model_id' or both 'features' and 'model_plan'."
        },
    )
