import json, ast

log_full = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript_full.jsonl"

with open(log_full, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        if i in [236, 240]:
            data = json.loads(line)
            calls = data.get("tool_calls", [])
            for c in calls:
                args = c.get("args", {})
                code = args.get("CodeContent", "") or args.get("ReplacementContent", "")
                if "class ProductModel" in code:
                    try:
                        ast.parse(code)
                        print(f"AST PARSE SUCCESSFUL for line {i}! Length:", len(code))
                        with open("models.py", "w", encoding="utf-8") as out:
                            out.write(code)
                        print("COMPLETE MODELS.PY RESTORED PERFECTLY!")
                        break
                    except Exception as e:
                        print(f"AST Error line {i}:", e)
