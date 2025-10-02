from fastapi import APIRouter
from app.models.preflight import Preflight
from uuid import uuid4

router = APIRouter(prefix="/preflight", tags=["preflight"])


@router.post("", summary="Validate drawing meta and return normalized info")
def do_preflight(payload: Preflight):
    preflight_id = str(uuid4())
    return {
        "ok": True,
        "preflight_id": preflight_id,
        "normalized": payload.model_dump(),
    }
