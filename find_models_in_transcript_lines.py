import json

log_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript.jsonl"

found_lines = []
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        if "class ProductModel" in line and "class ReportModel" in line:
            found_lines.append((i, line))

print("Found lines count:", len(found_lines))
for i, line in found_lines:
    print(f"Line {i}, len={len(line)}")

if found_lines:
    # Get last line
    i, line = found_lines[-1]
    data = json.loads(line)
    calls = data.get("tool_calls", [])
    for c in calls:
        args = c.get("args", {})
        code = args.get("CodeContent", "")
        if "class ProductModel" in code and "class ReportModel" in code:
            with open("models.py", "w", encoding="utf-8") as out:
                out.write(code)
            print(f"Saved complete models.py from line {i}! Length: {len(code)}")
            break
