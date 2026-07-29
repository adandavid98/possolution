from PIL import Image
import os

# Let's inspect media__1784821479886.png (size 1024, 541)
img_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded\media__1784821479886.png"
if os.path.exists(img_path):
    img = Image.open(img_path)
    w, h = img.size
    print("Full image size:", (w, h))

    # On the login screen:
    # Left dark card occupies roughly x=80 to x=480, y=100 to y=440
    # Let's crop the login emblem in the upper center of left hero card:
    # x: 180 to 380, y: 140 to 340
    logo_crop = img.crop((180, 140, 380, 340))
    logo_crop.convert("RGB").save("assets/logo.jpg")
    print("Extracted exact previous logo to assets/logo.jpg!")
