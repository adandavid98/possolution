import json

log_file = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript_full.jsonl"

found_blocks = []
with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "class ProductModel" in line and "class VentaModel" in line:
            found_blocks.append(line)

print("Found transcript blocks:", len(found_blocks))
if found_blocks:
    # Extract code from json line
    data = json.loads(found_blocks[-1])
    # Search in tool calls or content
    content_str = json.dumps(data)
    idx = content_str.find("class UserModel:")
    if idx != -1:
        print("Found class UserModel in transcript!")
        # Print slice around models.py
        snippet = content_str[idx:idx+12000]
        # Clean up json unescaping
        cleaned = snippet.encode('utf-8').decode('unicode_escape')
        with open("recovered_models.py", "w", encoding="utf-8") as out:
            out.write(cleaned)
        print("Saved recovered_models.py!")
