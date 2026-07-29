import os

log_dir = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2"

for root, dirs, files in os.walk(log_dir):
    for fname in files:
        if fname.endswith(('.log', '.jsonl', '.txt')):
            p = os.path.join(root, fname)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "class ProductModel" in content and "class VentaModel" in content:
                        print("Found in file:", p, "size:", len(content))
                        # Find indices
                        idx1 = content.find("class ProductModel:")
                        idx2 = content.find("class VentaModel:")
                        print("  Indices:", idx1, idx2)
            except Exception:
                pass
