import json, ast

log_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated/logs/transcript_full.jsonl"

best_code = ""

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "models.py" in line and "class ProductModel" in line:
            try:
                data = json.loads(line)
                # Look in tool_calls for write_to_file or replace_file_content
                calls = data.get("tool_calls", [])
                for c in calls:
                    args = c.get("args", {})
                    code = args.get("CodeContent", "") or args.get("ReplacementContent", "")
                    if "class ProductModel" in code and "class VentaModel" in code:
                        try:
                            ast.parse(code)
                            print("VALID PYTHON AST FOUND! Length:", len(code))
                            best_code = code
                        except Exception:
                            pass
            except Exception:
                pass

if best_code:
    with open("models.py", "w", encoding="utf-8") as out:
        out.write(best_code)
    print("models.py successfully restored and validated!")
else:
    print("Searching transcript.jsonl for complete write_to_file of models.py...")
    log_path2 = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated/logs/transcript.jsonl"
    with open(log_path2, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "models.py" in line and "class ProductModel" in line:
                try:
                    data = json.loads(line)
                    calls = data.get("tool_calls", [])
                    for c in calls:
                        args = c.get("args", {})
                        code = args.get("CodeContent", "")
                        if "class ProductModel" in code and "class VentaModel" in code:
                            try:
                                ast.parse(code)
                                print("VALID AST FOUND IN transcript.jsonl! Length:", len(code))
                                best_code = code
                            except Exception:
                                pass
                except Exception:
                    pass
    if best_code:
        with open("models.py", "w", encoding="utf-8") as out:
            out.write(best_code)
        print("models.py successfully restored and validated!")
