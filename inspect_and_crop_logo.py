from PIL import Image
import os

# Let's inspect media__1784771302387.png or media__1784821479886.png
img = Image.open(r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded\media__1784771302387.png")
print("Image size:", img.size)

# The login card logo is centered on the login screen
# Crop center card area
w, h = img.size
# Crop login logo area (~ x: 380-640, y: 150-380)
logo_crop = img.crop((380, 160, 640, 420))
logo_crop.save(r"c:\Users\Adan\Documents\Anti-POS_Project\cropped_test.png")
print("Saved cropped_test.png")
