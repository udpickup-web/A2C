from __future__ import annotations

import os
import uuid
from typing import Dict, Optional, Tuple

from fastapi import FastAPI, APIRouter, Depends, Header, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

from .schemas import (
    PreflightIn,
    PreflightOut,
    ViewsIn,
    ViewsOut,
    PlanIn,
    PlanOut,
    BuildIn,
    BuildOut,
    Sketch2DIn,
    Sketch2DOut,
)
from .utils import polygon_area, bbox_from_points
from .errors import (
    error_payload,
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")


def get_app_env() -> str:
    return os.getenv("APP_ENV", "dev").lower()


def get_cors_origins() -> list[str]:
    if get_app_env() != "prod":
        return ["*"]
    raw = os.getenv("CORS_ORIGINS", "")
    return [x.strip() for x in raw.split(",") if x.strip()]


def is_auth_required() -> bool:
    if os.getenv("AUTH_REQUIRED", "") in ("1", "true", "yes"):
        return True
    return get_app_env() == "prod"


def get_max_body_bytes() -> int:
    mb = int(os.getenv("MAX_BODY_MB", "10"))
    return mb * 1024 * 1024


# ---------- App ----------

app = FastAPI(
    title="Core API (TZ v1) вЂ” mobile-first",
    version="1.1.0",
    description="Р‘СЌРєРµРЅРґ СЃ РїСЂРµС„РёРєСЃРѕРј /api/v1, РµРґРёРЅС‹Рј РєРѕРЅС‚СЂР°РєС‚РѕРј РѕС€РёР±РѕРє Рё stub-СЌРєСЃРїРѕСЂС‚РѕРј Р°СЂС‚РµС„Р°РєС‚РѕРІ.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static artifacts mount
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
app.mount("/artifacts", StaticFiles(directory=ARTIFACTS_DIR), name="artifacts")

# Exception handlers (unified error envelope)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# ---------- Middleware: X-Request-Id, JSON empty-body/size guard ----------


@app.middleware("http")
async def request_context_mw(request: Request, call_next):
    # X-Request-Id
    req_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    # Size limit
    body_bytes = b""
    if request.method in ("POST", "PUT", "PATCH"):
        try:
            body_bytes = await request.body()
        except Exception:
            # Will be handled by parser later; keep as empty
            body_bytes = b""

        if len(body_bytes) > get_max_body_bytes():
            return JSONResponse(
                status_code=413,
                content=error_payload(
                    413, "Request body too large", {"max_bytes": get_max_body_bytes()}
                ),
            )

        ctype = request.headers.get("content-type", "")
        if "application/json" in ctype and (body_bytes.strip() in (b"", b"null")):
            return JSONResponse(status_code=400, content=error_payload(400, "Empty JSON body", {}))
        path = request.url.path
        JSON_REQUIRED_PREFIXES = (
            "/api/v1/preflight",
            "/api/v1/views",
            "/api/v1/register",
            "/api/v1/plan",
            "/api/v1/build",
            "/api/v1/sketch2d",
            "/api/v1/export",
        )
        if request.method in ("POST", "PUT", "PATCH"):
            # /upload — Multipart, для остальных из списка обязателен JSON
            if path.startswith(JSON_REQUIRED_PREFIXES) and not path.startswith("/api/v1/upload"):
                if "application/json" not in ctype.lower():
                    return JSONResponse(
                        status_code=415,
                        content=error_payload(
                            415, "Unsupported Media Type", {"expected": "application/json"}
                        ),
                    )

        # Re-inject body into request stream
        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        request._receive = receive  # type: ignore[attr-defined]

    response = await call_next(request)
    response.headers["X-Request-Id"] = req_id
    return response


# ---------- Auth dependency ----------


def bearer_auth(authorization: Optional[str] = Header(default=None)):
    if not is_auth_required():
        return
    if not authorization or not authorization.lower().startswith("bearer "):
        raise StarletteHTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    expected = os.getenv("AUTH_TOKEN", "")
    if expected and token != expected:
        raise StarletteHTTPException(status_code=401, detail="Invalid token")


# ---------- Router with prefix /api/v1 ----------

router = APIRouter(prefix="/api/v1", dependencies=[Depends(bearer_auth)])


@router.get("/healthz", tags=["meta"])
def healthz():
    return {"status": "ok"}


# ---------- /preflight ----------


@router.post("/preflight", response_model=PreflightOut, tags=["preflight"])
def preflight(inp: PreflightIn):
    a, b = (int(x) for x in inp.scale.split(":"))
    scale_ratio = a / b if b else 1.0
    normalized = {
        "standard": inp.standard,
        "projection": inp.projection,
        "units": inp.units,
        "scale_ratio": scale_ratio,
        "page_wh_px": [inp.page.w_px, inp.page.h_px],
    }
    return PreflightOut(**inp.model_dump(), preflight_id=str(uuid.uuid4()), normalized=normalized)


# ---------- /views ----------


@router.post("/views", response_model=ViewsOut, tags=["views"])
def views(inp: ViewsIn):
    areas: Dict[str, float] = {}
    solved_aggr = {"outer": True, "holes": True, "slots": True, "arcs": True}
    holes_total = 0
    for v in inp.views:
        areas[v.id] = polygon_area(v.sketch.outer_polygon_px)
        holes_total += len(v.sketch.holes_px or [])
        for key in ["outer", "holes", "slots", "arcs"]:
            flag = getattr(v.sketch.solved, key, True)
            if flag is None:
                flag = True
            solved_aggr[key] = bool(solved_aggr[key] and flag)
    stats = {
        "views_count": len(inp.views),
        "holes_total": holes_total,
        "avg_area": (sum(areas.values()) / len(areas)) if areas else 0.0,
    }
    return ViewsOut(views_count=len(inp.views), areas=areas, solved_all=solved_aggr, stats=stats)


# ---------- /sketch2d ----------


@router.post("/sketch2d", response_model=Sketch2DOut, tags=["sketch"])
def sketch2d(inp: Sketch2DIn):
    bbox = bbox_from_points(inp.sketch.outer_polygon_px)
    return Sketch2DOut(sketch_id=str(uuid.uuid4()), bbox_px=bbox)


# ---------- /plan ----------


@router.post("/plan", response_model=PlanOut, tags=["plan"])
def plan(inp: PlanIn):
    return PlanOut(**inp.model_dump(), plan_id=str(uuid.uuid4()))


# ---------- /build ----------


@router.post("/build", response_model=BuildOut, tags=["build"])
def build(inp: BuildIn):
    hist: Dict[str, int] = {}
    for f in inp.features:
        hist[f.type] = hist.get(f.type, 0) + 1
    notes = "OK"
    return BuildOut(
        build_id=str(uuid.uuid4()),
        features_count=len(inp.features),
        types_histogram=hist,
        notes=notes,
    )


# ---------- /register (views + preflight -> anchors + views) ----------


class ViewsAnchorsOut(JSONResponse):
    pass


@router.post("/register", tags=["register"])
def register(payload: Dict):
    # Payload MUST contain "views" and "preflight"
    if "views" not in payload or "preflight" not in payload:
        raise StarletteHTTPException(
            status_code=400, detail="Expected payload with 'views' and 'preflight'"
        )
    try:
        views_in = ViewsIn(**payload["views"])
        preflight_in = PreflightIn(**payload["preflight"])
    except Exception as e:
        # Let Pydantic/handlers render 422 if shape is wrong
        raise e

    anchors: Dict[str, Dict[str, Tuple[float, float]]] = {}
    for v in views_in.views:
        xs = [p[0] for p in v.sketch.outer_polygon_px]
        ys = [p[1] for p in v.sketch.outer_polygon_px]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        cx = (bbox[0] + bbox[2]) / 2.0
        cy = (bbox[1] + bbox[3]) / 2.0
        anchors[v.id] = {
            "origin_px": (bbox[0], bbox[1]),
            "center_px": (cx, cy),
        }
    out = {
        "views_anchors": anchors,
        "views": views_in.model_dump(),
        "preflight": preflight_in.model_dump(),
    }
    return JSONResponse(out)


# ---------- /export (features+plan OR model_id) ----------


@router.post("/export", tags=["export"])
def export_api(payload: Dict):
    # Validate either {model_id} or {features, plan}
    model_id = payload.get("model_id")
    features = payload.get("features")
    plan = payload.get("plan")
    if not model_id and not (features and plan):
        raise StarletteHTTPException(
            status_code=400, detail="Provide either 'model_id' or both 'features' and 'plan'"
        )

    export_id = str(uuid.uuid4())
    exp_dir = os.path.join(ARTIFACTS_DIR, export_id)
    os.makedirs(exp_dir, exist_ok=True)
    # Create stub files
    for name in ("model.step", "model.stl", "model.glb"):
        with open(os.path.join(exp_dir, name), "wb") as f:
            f.write(b"stub-artifact")
    base_url = f"/artifacts/{export_id}"
    report = {
        "id": export_id,
        "source": "model_id" if model_id else "features+plan",
        "counts": {
            "features": len(features.get("features", [])) if isinstance(features, dict) else None
        },
    }
    return JSONResponse(
        {
            "step_url": f"{base_url}/model.step",
            "stl_url": f"{base_url}/model.stl",
            "glb_url": f"{base_url}/model.glb",
            "export_report": report,
        }
    )


# ---------- /upload (multipart) ----------


@router.post("/upload", tags=["upload"])
async def upload(file: UploadFile = File(...)):
    # Save to artifacts
    upload_id = str(uuid.uuid4())
    dirp = os.path.join(ARTIFACTS_DIR, upload_id)
    os.makedirs(dirp, exist_ok=True)
    path = os.path.join(dirp, file.filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return {
        "upload_id": upload_id,
        "filename": file.filename,
        "size": len(content),
        "url": f"/artifacts/{upload_id}/{file.filename}",
    }


# Include router
app.include_router(router)


# Root (non-prefixed) for quick info
@app.get("/", tags=["meta"])
def root():
    return {"ok": True, "service": "core-api", "version": "1.1.0", "prefix": "/api/v1"}
