import json

log_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript.jsonl"

all_models_calls = []

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        if "TargetFile" in line and "models.py" in line:
            try:
                data = json.loads(line)
                calls = data.get("tool_calls", [])
                for c in calls:
                    args = c.get("args", {})
                    if args.get("TargetFile", "").endswith("models.py"):
                        code = args.get("CodeContent", "") or args.get("ReplacementContent", "")
                        all_models_calls.append((i, len(code), code))
            except Exception:
                pass

print(f"Total write calls targeting models.py: {len(all_models_calls)}")
for i, l, code in all_models_calls:
    print(f"Line {i}, len {l}: ProductModel={'ProductModel' in code}, UserModel={'UserModel' in code}, CajaModel={'CajaModel' in code}")
