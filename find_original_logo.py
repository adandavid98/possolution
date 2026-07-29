import os
from PIL import Image

user_up_dir = r'C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded'
for f in os.listdir(user_up_dir):
    if f.endswith('.png'):
        p = os.path.join(user_up_dir, f)
        try:
            im = Image.open(p)
            print(f"{f}: size={im.size}, mode={im.mode}")
        except Exception:
            pass
