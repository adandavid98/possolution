from PIL import Image

# Let's inspect media__1785272187860.png
img = Image.open(r"C:\Users\Adan\.gemini\antigravity\brain\b9fa430f-b95a-4f53-a66e-abcf647967d2\.user_uploaded\media__1785272187860.png")
print("Size of media__1785272187860.png:", img.size)

# Let's crop the login hero image area (around x: 140 to 360, y: 160 to 360)
logo_area = img.crop((140, 160, 360, 360))
logo_area.convert("RGB").save("assets/logo.jpg")
print("Extracted exact logo from media__1785272187860.png into assets/logo.jpg!")
