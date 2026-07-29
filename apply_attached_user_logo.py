import os
from PIL import Image

attached_img_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded\media__1785274810319.png"
target_jpg = r"assets/logo.jpg"

if os.path.exists(attached_img_path):
    img = Image.open(attached_img_path)
    img.convert("RGB").save(target_jpg, "JPEG", quality=100)
    print("EXACT user attached logo copied to assets/logo.jpg!")
else:
    print("Attached image not found at:", attached_img_path)
