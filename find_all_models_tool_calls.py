import json

log_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript.jsonl"

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        if "models.py" in line:
            try:
                data = json.loads(line)
                calls = data.get("tool_calls", [])
                for c in calls:
                    args = c.get("args", {})
                    tf = args.get("TargetFile", "")
                    if tf.endswith("models.py"):
                        code = args.get("CodeContent", "") or args.get("ReplacementContent", "")
                        print(f"Line {i}, tool: {c.get('name')}, code len: {len(code)}, contains ProductModel: {'ProductModel' in code}, contains UserModel: {'UserModel' in code}")
            except Exception:
                pass
