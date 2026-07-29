from PIL import Image

img = Image.open(r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded\media__1784771302387.png")
# In media__1784771302387.png (size 1024, 534):
# Left half is 0 to 512.
# Let's crop x: 150 to 350, y: 120 to 320:
logo_crop = img.crop((150, 120, 350, 320))
logo_crop.convert("RGB").save("assets/logo.jpg")
print("Cropped logo from (150, 120, 350, 320) and saved to assets/logo.jpg")
