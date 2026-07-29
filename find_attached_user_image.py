import os
from PIL import Image

user_up_dir = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded"
files = sorted(os.listdir(user_up_dir))
latest_files = files[-5:]
print("Latest uploaded files:")
for f in latest_files:
    p = os.path.join(user_up_dir, f)
    try:
        im = Image.open(p)
        print(f, im.size, im.mode)
    except Exception as e:
        print(f, e)
