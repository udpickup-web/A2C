from __future__ import annotations
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List


def _pm_header(name: str, value: str) -> Dict[str, str]:
    return {"key": name, "value": value}


def _request_from_op(method: str, url_path: str, op: Dict[str, Any]) -> Dict[str, Any]:
    name = op.get("summary") or f"{method.upper()} {url_path}"
    headers = [
        _pm_header("Content-Type", "application/json"),
        _pm_header("Authorization", "Bearer {{token}}"),
    ]
    req: Dict[str, Any] = {
        "name": name,
        "request": {
            "method": method.upper(),
            "header": headers,
            "url": {
                "raw": "{{baseUrl}}" + url_path,
                "host": ["{{baseUrl}}"],
                "path": [p for p in url_path.lstrip("/").split("/")],
            },
        },
    }
    rb = op.get("requestBody", {}).get("content", {}).get("application/json", {})
    example = rb.get("example") or (rb.get("examples") or {})
    example_value = None
    if isinstance(example, dict) and example:
        first = next(iter(example.values()))
        if isinstance(first, dict):
            example_value = first.get("value")
    if example_value is None and method.lower() in ("post", "put", "patch"):
        example_value = {}
    if example_value is not None:
        req["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(example_value, ensure_ascii=False, indent=2),
            "options": {"raw": {"language": "json"}},
        }
    return req


def main() -> None:
    openapi_path = Path("collections/openapi.json")
    if not openapi_path.exists():
        raise SystemExit(
            "[ERROR] collections/openapi.json not found. Run tools/generate_openapi.py first."
        )
    schema = json.loads(openapi_path.read_text(encoding="utf-8"))
    items: List[Dict[str, Any]] = []

    paths: Dict[str, Any] = schema.get("paths", {})
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for url_path, methods in paths.items():
        for method, op in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete"):
                continue
            tags = op.get("tags") or ["default"]
            for tag in tags:
                grouped.setdefault(tag, []).append(_request_from_op(method, url_path, op))

    for tag, reqs in grouped.items():
        items.append({"name": tag, "item": reqs})

    pm = {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": "Analog2CAD API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "description": "Generated from OpenAPI",
        },
        "item": items,
        "variable": [
            {"key": "baseUrl", "value": "http://127.0.0.1:8011"},
            {"key": "token", "value": "demo"},
        ],
    }

    out_dir = Path("collections/postman")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "Analog2CAD.postman_collection.json"
    out_path.write_text(json.dumps(pm, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Postman collection saved to {out_path}")


if __name__ == "__main__":
    main()
