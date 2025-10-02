import httpx, json, pathlib

BASE = "http://127.0.0.1:8001"

def post_json(path: str, data_path: str):
    data = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    r = httpx.post(BASE + path, json=data, timeout=10)
    r.raise_for_status()
    print(path, "->", r.json())

def main():
    post_json("/preflight", "samples/preflight.json")
    post_json("/views", "samples/views.json")
    post_json("/plan", "samples/model_plan.json")
    post_json("/build", "samples/features.json")

if __name__ == "__main__":
    main()
