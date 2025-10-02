from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import Request

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/openapi", summary="Return OpenAPI spec JSON")
def export_openapi(request: Request):
    return JSONResponse(request.app.openapi())
