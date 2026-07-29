import os
from PIL import Image

# Let's inspect media__1784771302387.png which was uploaded early in the session
img_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded\media__1784771302387.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    # The logo was at the center of the login screen card
    # Let's crop the login emblem logo (around 412, 168 to 612, 368)
    logo_crop = img.crop((412, 168, 612, 368))
    logo_crop.convert("RGB").save(r"assets/logo.jpg")
    print("Original Minimarket logo restored to assets/logo.jpg!")
else:
    print("Screenshot not found at:", img_path)
