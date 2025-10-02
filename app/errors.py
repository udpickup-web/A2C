from __future__ import annotations
from typing import Any, Dict
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def error_payload(code: int, message: str, details: Any = None) -> Dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details or {}}}


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 422 Unprocessable Entity
    return JSONResponse(
        status_code=422, content=error_payload(422, "Validation error", exc.errors())
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Map Starlette/FastAPI HTTPException into our envelope
    return JSONResponse(
        status_code=exc.status_code, content=error_payload(exc.status_code, str(exc.detail), {})
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    # 500 Internal Server Error (do not leak details)
    return JSONResponse(status_code=500, content=error_payload(500, "Internal server error", {}))
