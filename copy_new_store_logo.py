import os
import shutil
from PIL import Image

gen_store_logo = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\minimarket_logo_1785272233786.jpg"
target_jpg = r"assets/logo.jpg"

if os.path.exists(gen_store_logo):
    img = Image.open(gen_store_logo)
    img.save(target_jpg, "JPEG", quality=95)
    print("New clean Minimarket logo copied to assets/logo.jpg!")
else:
    print("Store logo file not found:", gen_store_logo)
