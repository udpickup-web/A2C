from __future__ import annotations
import json
from pathlib import Path


def main() -> None:
    openapi_path = Path("collections/openapi.json")
    if not openapi_path.exists():
        raise SystemExit(
            "[ERROR] collections/openapi.json not found. Run tools/generate_openapi.py first."
        )
    data = json.loads(openapi_path.read_text(encoding="utf-8"))
    base_dir = Path("collections/bruno/Analog2CAD/collections")
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "collection.bru").write_text(
        'type: collection\nname: Analog2CAD\nversion: "1.0"\n', encoding="utf-8"
    )

    for url_path, methods in data.get("paths", {}).items():
        for method, op in methods.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete"):
                continue
            name = op.get("summary") or f"{method.upper()} {url_path}"
            file_name = f"{method}_{url_path.strip('/').replace('/', '_') or 'root'}.bru"
            headers = [
                '  "Content-Type": "application/json"',
                '  "Authorization": "Bearer {{token}}"',
            ]
            body_raw = ""
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
                import json as _json

                body_raw = _json.dumps(example_value, ensure_ascii=False, indent=2)

            content = f"type: http\nname: {name}\nmethod: {method.upper()}\nurl: {{baseUrl}}{url_path}\nheaders: {{\n{',\n'.join(headers)}\n}}\nbody: {body_raw}"
            (base_dir / file_name).write_text(content, encoding="utf-8")

    env_dir = base_dir.parent / "environments"
    env_dir.mkdir(parents=True, exist_ok=True)
    env_dir.joinpath("local.bru").write_text(
        'type: environment\nname: local\nvars: {\n  "baseUrl": "http://127.0.0.1:8011",\n  "token": "demo"\n}\n',
        encoding="utf-8",
    )
    print(f"[OK] Bruno collection written to {base_dir}")


if __name__ == "__main__":
    main()
