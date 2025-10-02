from fastapi import APIRouter
from app.models.views import Views

router = APIRouter(prefix="/views", tags=["views"])


@router.post("", summary="Accept 2D views and sketches")
def submit_views(payload: Views):
    ids = [v.id for v in payload.views]
    stats = {
        "count": len(payload.views),
        "ids": ids,
        "solved_flags": {v.id: v.sketch.solved.model_dump() for v in payload.views},
    }
    return {"ok": True, "stats": stats}
