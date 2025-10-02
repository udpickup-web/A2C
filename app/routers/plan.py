from fastapi import APIRouter
from app.models.model_plan import ModelPlan
from uuid import uuid4

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post("", summary="Register a modeling plan / build order")
def submit_plan(payload: ModelPlan):
    plan_id = str(uuid4())
    return {"ok": True, "plan_id": plan_id, "plan": payload.model_dump()}
