import json, re

log_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript.jsonl"

matches = []
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        if "models.py" in line and "CodeContent" in line:
            matches.append((i, line))

print("Found matches count:", len(matches))
for i, line in matches:
    try:
        data = json.loads(line)
        calls = data.get("tool_calls", [])
        for c in calls:
            args = c.get("args", {})
            if args.get("TargetFile", "").endswith("models.py"):
                code = args.get("CodeContent", "")
                print(f"Line {i}: code len={len(code)}, has ProductModel={'ProductModel' in code}, has UserModel={'UserModel' in code}")
                if len(code) > 10000:
                    with open("models.py", "w", encoding="utf-8") as out:
                        out.write(code)
                    print("--> Saved complete models.py! Length:", len(code))
                    break
    except Exception as e:
        print(f"Line {i} parse error:", e)
