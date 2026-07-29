import os
from PIL import Image

# Let's inspect media__1784771302387.png
img_path = r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded\media__1784771302387.png"
img = Image.open(img_path)
print("Image size:", img.size)

# Let's save smaller chunks of the screenshot to check where the login logo is
# Crop left panel of login screen (around x: 100 to 500, y: 100 to 450)
left_hero = img.crop((100, 100, 500, 450))
left_hero.save("left_hero_debug.png")
print("Saved left_hero_debug.png")
