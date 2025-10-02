from __future__ import annotations
import json
import sys
import importlib
from pathlib import Path


def main() -> None:
    # Ensure project root on sys.path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        app_module = importlib.import_module("app.main")
        app = getattr(app_module, "app")
    except Exception as e:
        raise SystemExit(f"[ERROR] Cannot import app.main: {e}") from e

    schema = app.openapi()
    out_dir = Path("collections")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "openapi.json"
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] OpenAPI exported to {out_path}")


if __name__ == "__main__":
    main()
