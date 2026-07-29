import os
import json

transcript_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.system_generated\logs\transcript_full.jsonl"

found_models = []
if os.path.exists(transcript_path):
    with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if 'class ProductModel' in line or 'class VentaModel' in line:
                print("Found match in transcript line length:", len(line))
                found_models.append(line)

print(f"Total matches: {len(found_models)}")
