import os
from PIL import Image, ImageDraw, ImageFont

def draw_flat_minimal_icon():
    # Base size 512x512 for max crispness
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Dark Slate Container (Background Squircle)
    margin = 16
    bg_box = [margin, margin, size - margin, size - margin]
    draw.rounded_rectangle(bg_box, radius=96, fill=(15, 23, 42, 255)) # Dark Navy #0F172A

    # 2. Main Blue Squircle Emblem
    emblem_margin = 48
    emblem_box = [emblem_margin, emblem_margin, size - emblem_margin, size - emblem_margin]
    draw.rounded_rectangle(emblem_box, radius=80, fill=(37, 99, 235, 255)) # Royal Blue #2563EB

    # 3. Inner White Geometric 'P' Logo (Minimalist Point of Sale Emblem)
    # Stem of 'P'
    stem_x1, stem_y1 = 170, 140
    stem_x2, stem_y2 = 230, 370
    draw.rounded_rectangle([stem_x1, stem_y1, stem_x2, stem_y2], radius=16, fill=(255, 255, 255, 255))

    # Loop of 'P'
    loop_box = [170, 140, 350, 270]
    draw.rounded_rectangle(loop_box, radius=65, fill=(255, 255, 255, 255))
    
    # Inner Cutout of 'P' loop
    inner_cutout = [230, 185, 295, 225]
    draw.rounded_rectangle(inner_cutout, radius=20, fill=(37, 99, 235, 255))

    # Clean Accent Bar (Minimalist POS card / terminal slot detail)
    accent_box = [170, 310, 340, 345]
    draw.rounded_rectangle(accent_box, radius=12, fill=(255, 255, 255, 255))

    # Save as multi-size ICO file
    ico_dest = r"C:\Users\Adan\Documents\Anti-POS_Project\assets\app_icon.ico"
    
    # Create sizes
    ico_sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    img.save(ico_dest, format="ICO", sizes=ico_sizes)
    print(f"Pure flat minimalist app_icon.ico generated successfully at: {ico_dest}")

if __name__ == "__main__":
    draw_flat_minimal_icon()
