import json, re

transcript_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript.jsonl"

all_models_code = ""

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "from database import execute_query" in line and "class ProductModel" in line:
            # Parse json line
            try:
                data = json.loads(line)
                content = json.dumps(data)
                # Find models code block
                start = content.find("from database import execute_query")
                end = content.rfind("ALL_MODULES =")
                if start != -1 and end != -1:
                    raw_sub = content[start:end+50]
                    # Unescape json
                    clean_sub = json.loads('"' + raw_sub.replace('"', '\\"') + '"')
                    all_models_code = raw_sub
            except Exception:
                pass

print("Code length found:", len(all_models_code))
if len(all_models_code) > 1000:
    # Decode double escape
    unescaped = all_models_code.encode().decode('unicode_escape')
    with open("models.py", "w", encoding="utf-8") as out:
        out.write(unescaped)
    print("models.py written! Length:", len(unescaped))
