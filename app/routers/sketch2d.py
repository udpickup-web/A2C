from fastapi import APIRouter
from app.models.views import Views

router = APIRouter(prefix="/sketch2d", tags=["sketch2d"])

@router.post("", summary="Run 2D sketch solver on provided views")
def run_sketch_solver(payload: Views):
    # Stub: pretend we solved constraints successfully
    result = {v.id: {"outer": True, "holes": True, "slots": True, "arcs": True} for v in payload.views}
    return {"ok": True, "result": result}
