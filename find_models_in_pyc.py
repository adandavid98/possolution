import os

pycache_dir = r"c:\Users\Adan\Documents\Anti-POS_Project\__pycache__"
if os.path.exists(pycache_dir):
    for f in os.listdir(pycache_dir):
        if f.startswith("models."):
            print("Found models pyc:", f)
            p = os.path.join(pycache_dir, f)
            print("pyc size:", os.path.getsize(p))
