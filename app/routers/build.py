from fastapi import APIRouter
from pydantic import BaseModel
from app.models.features import Features
from app.models.model_plan import ModelPlan
from typing import Optional
from uuid import uuid4

router = APIRouter(prefix="/build", tags=["build"])

class BuildRequest(BaseModel):
    features: Features
    plan: Optional[ModelPlan] = None

@router.post("", summary="Start build process from features (and plan)")
def start_build(payload: BuildRequest):
    build_id = str(uuid4())
    steps = len(payload.features.features)
    return {"ok": True, "build_id": build_id, "steps": steps}
