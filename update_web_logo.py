import os
import shutil
from PIL import Image

gen_web_logo = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\web_app_logo_1785274547701.jpg"
target_jpg = r"assets/logo.jpg"

if os.path.exists(gen_web_logo):
    img = Image.open(gen_web_logo)
    img.save(target_jpg, "JPEG", quality=95)
    print("New web logo updated at assets/logo.jpg!")
else:
    print("Generated web logo file not found:", gen_web_logo)
