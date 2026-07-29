import json, re

log_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript.jsonl"

found_str = ""
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "TargetFile" in line and "models.py" in line and "CodeContent" in line:
            print("Found models.py write_to_file entry in transcript!")
            try:
                data = json.loads(line)
                # Search inside tool_calls
                tool_calls = data.get("tool_calls", [])
                for tc in tool_calls:
                    args = tc.get("args", {})
                    if "TargetFile" in args and "models.py" in args["TargetFile"]:
                        code = args.get("CodeContent", "")
                        if "class ProductModel" in code:
                            found_str = code
                            print("Found full ProductModel code content! Length:", len(code))
            except Exception as e:
                print("Error parsing json line:", e)

if not found_str:
    # Fallback search by string matching
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        full_text = f.read()
        m = re.findall(r'from database import execute_query.*?(?=class ALL_MODULES|ALL_MODULES =|\Z)', full_text, re.DOTALL)
        for snippet in m:
            if "class ProductModel" in snippet and "class VentaModel" in snippet:
                found_str = snippet
                break

if found_str:
    # Clean string if needed
    cleaned = found_str.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
    with open("models.py", "w", encoding="utf-8") as out:
        out.write(cleaned)
    print("models.py restored successfully! File size:", len(cleaned))
else:
    print("Could not extract models.py code content.")
