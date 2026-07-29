import json, ast

log_full = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript_full.jsonl"

with open(log_full, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        if "class ProductModel" in line:
            try:
                data = json.loads(line)
                calls = data.get("tool_calls", [])
                for c in calls:
                    args = c.get("args", {})
                    code = args.get("CodeContent", "")
                    if "class ProductModel" in code and "class UserModel" in code:
                        print(f"Line {i}: tool={c.get('name')}, code len={len(code)}")
                        try:
                            ast.parse(code)
                            print("  --> AST VALID! Saving models.py...")
                            with open("models.py", "w", encoding="utf-8") as out:
                                out.write(code)
                            print("  Saved successfully!")
                            break
                        except Exception as e:
                            print("  AST error:", e)
            except Exception:
                pass
