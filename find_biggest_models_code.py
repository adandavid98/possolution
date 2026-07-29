import json, ast

log_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript.jsonl"

found_str = ""

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "class CustomerModel" in line and "class ReportModel" in line:
            print("Found line with CustomerModel and ReportModel!")
            try:
                data = json.loads(line)
                calls = data.get("tool_calls", [])
                for c in calls:
                    args = c.get("args", {})
                    code = args.get("CodeContent", "")
                    if "class CustomerModel" in code and "class ReportModel" in code:
                        found_str = code
                        break
            except Exception:
                pass

if found_str:
    with open("models.py", "w", encoding="utf-8") as out:
        out.write(found_str)
    print("RESTORED COMPLETE MODELS.PY! Length:", len(found_str))
else:
    print("No complete block found directly in json lines.")
